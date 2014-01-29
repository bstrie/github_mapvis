$(document).ready(function() {
  MIN_RADIUS = 2.5;
  THE_MOON = {lat: -50,
              lon: 0};
  TRANSITION_DURATION = 500;
  DOT_OPACITY = 0.2;

  function shrinken(val) {
    r = Math.pow(val, 1/4.1);
    if (r < MIN_RADIUS) { return MIN_RADIUS; }
    else { return r; }
  }

  function moonify(coords) {
    if (coords.lat === 'MOON') {
      return [THE_MOON.lon, THE_MOON.lat];
    }
    else {
      return [coords.lon, coords.lat];
    }
  }

  var projection = d3.geo.winkel3().translate([500, 300]).scale(195);

  var path = d3.geo.path().projection(projection);

  var map = d3.select('#map').append('svg');

  d3.json('world.json', function(error, world) {
    map.insert('path')
       .datum(topojson.object(world, world.objects.land))
       .attr('class', 'continents')
       .attr('d', path);

    map.insert('path')
       .datum(topojson.mesh(world, world.objects.countries, function(a, b) {
         return a.id !== b.id;
       }))
       .attr('class', 'countries')
       .attr('d', path);

    d3.json('data/newest.json', function(json) {
      map.selectAll('dots')
         .data(json, function(d) { return d.name })
         .enter()
         .append('svg:g')
         .attr('data-name', function(d) { return d.name })
         .attr('data-impact', function(d) { return d.impact })
         .attr('data-location', function(d) { return d.location })
         .attr('data-x', function(d) { return projection(moonify(d))[0] })
         .attr('data-y', function(d) { return projection(moonify(d))[1] })
         .attr('transform', function(d) {
           return 'translate(' + projection(moonify(d)).join(',') + ')';
         })
         .append('svg:circle')
         .attr('r', 0)
         .attr('fill-opacity', 0)
         .transition()
         .duration(TRANSITION_DURATION)
         .attr('r', function(d) { return shrinken(d.impact) })
         .attr('fill-opacity', DOT_OPACITY);
      interactify();
    });
  });

  function interactify() {
    // We get the offset of '#container' rather than 'svg' here because Firefox
    // puts an implicit margin around our SVG element.
    // As long as the intervening paddings and margins are 0, it should work.
    var offset = $('#container').offset();
    console.log(offset);
    $('svg').mousemove(function(e) {
      //console.log((e.pageX - offset.left) + ', ' + (e.pageY - offset.top));
    });
  }
});
