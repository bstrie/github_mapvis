#!/usr/bin/env python

import datetime
import getpass
import json
import requests
import shutil
import sys
import time

try:
    reponame = sys.argv[1]
    username = sys.argv[2]
except IndexError:
    print('Usage: get_data.py owner/repo username')
    print('Example: get_data.py mozilla/rust octocat')
    sys.exit(2)

password = getpass.getpass('Github password for {0}: '.format(username))
cred = (username, password)

# This next URL isn't technically a Github API, it's just convenient.
# If you're just doing tests, avoid abusing it by uncommenting the second line
# to get some representative test data.
# This is the only way to get additions and deletions for each user for a repo,
# but it will only return the top 100 users. We get the rest later.
#r = requests.get('https://github.com/{0}/graphs/contributors-data'.format(reponame))
r = requests.get('http://seleniac.org/map/data/test_data.json')
topcontributors = r.json()
print(topcontributors)
data = []
topnames = []

for user in topcontributors:
    name = user['author']['login']
    impact = 0
    for week in user['weeks']:
        impact += week['a'] + week['d']  # Impact is additions + deletions
    topnames.append(name)
    data.append({'name': name, 'impact': impact})

# Here's where we get the names of each user who wasn't in the top 100.
# Because we have no impact data, we just give them an impact of 1.
# The web page itself will ensure that their dot is large enough to be visible.
r = requests.get('https://api.github.com/repos/{0}/contributors'.format(reponame), auth=cred)
contributors = r.json()
for user in contributors:
    name = user['login']
    if name not in topnames:
        data.append({'name': name, 'impact': 1})

print(data)

# Now we look up each user in turn on Github, grab their location data,
# and run it through the Nominatim API.
for user in data:
    name = user['name']
    print(name)
    # This request is the reason we need authentication. Without it, Github
    # limits you to 60 requests per hour. Here's hoping your repo doesn't
    # have more than 4,999 contributors.
    r = requests.get('https://api.github.com/users/'+name, auth=cred)
    userdata = r.json()
    if 'location' in userdata:
        location = userdata['location'] or ''
    else:
        location = ''

    r = requests.get('http://open.mapquestapi.com/nominatim/v1/search.php',
                     params = {
                         'q': location,
                         'format': 'json',
                         'limit': '1'
                     },
                     headers = {'User-Agent': 'github.com/bstrie/github_mapvis crawler'})
    geodata = r.json()
    if not geodata:
        lat = 'MOON'
        lon = 'MOON'
    else:
        lat = geodata[0]['lat']
        lon = geodata[0]['lon']

    coords = {'name': name, 'location': location, 'lat': lat, 'lon': lon}
    print(coords)
    user.update(coords)
    time.sleep(0.5)  # To be a polite API consumer


# We sort it for silly reasons.
# D3 will draw the dots in order of appearance in the file.
# If large dots get drawn on top of small dots, it makes them harder to manually
# inspect via browser dev tools.
# Thus, we sort the data so that the large dots get drawn first.
data.sort(key=lambda x: x['impact'], reverse=True)

print(data)

date_filename = 'data/' + datetime.datetime.now().strftime('%Y%m%d_%H%M') + '.json'
with open(date_filename, 'w') as f:
    f.write(json.dumps(data))

shutil.copyfile(date_filename, 'data/newest.json')  # Destructive copy

print('Complete')
