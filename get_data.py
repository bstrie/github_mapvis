#!/usr/bin/env python

import getpass
import json
import requests
import sys
import time

filename = sys.argv[1]

username = sys.argv[2]
password = getpass.getpass('Github password for {0}: '.format(username))
cred = (username, password)

# This next URL isn't technically a Github API, it's just convenient.
# If you're just doing tests, avoid abusing it by uncommenting the second line
# to get some representative test data.
# This is the only way to get additions and deletions for each user for a repo,
# but it will only return the top 100 users. We get the rest later.
#r = requests.get('https://github.com/mozilla/rust/graphs/contributors-data')
r = requests.get('http://seleniac.org/map/contrib.json')
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

#print(data)

# Here's where we get the names of each user who wasn't in the top 100.
# Because we have no impact data, we just give them an impact of 1.
# The web page itself will ensure that their dot is large enough to be visible.
r = requests.get('https://api.github.com/repos/mozilla/rust/contributors', auth=cred)
contributors = r.json()
for user in contributors:
    name = user['login']
    if name not in topnames:
        data.append({'name': name, 'impact': 1})

print(data)

for user in data:
    name = user['name']
    print(name)
    r = requests.get('https://api.github.com/users/'+name, auth=cred)
    userdata = r.json()
    #print(userdata)
    if 'location' in userdata:
        location = userdata['location'] or ''
    else:
        location = ''

    r = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address='+location+'&sensor=false',
                      auth=cred)
    geodata = r.json()
    #print(geodata)
    if geodata['status'] != 'OK':
        lat = 'MOON'
        lon = 'MOON'
    else:
        lat = geodata['results'][0]['geometry']['location']['lat']
        lon = geodata['results'][0]['geometry']['location']['lng']

    coords = {'name': name, 'lat': lat, 'lon': lon}
    print(coords)
    user.update(coords)
    time.sleep(0.5)  # To be a polite API consumer

print(data)

with open('data/'+filename, 'w') as f:
    f.write(json.dumps(data))
