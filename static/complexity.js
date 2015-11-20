var m = [80, 50, 80, 50]; // margins
var w = 600- m[1] - m[3]; // width
var h = 400 - m[0] - m[2]; // height

d3.json("/complexity", function(error, full_data) {

  data = full_data['values']
  color = full_data['color']

  var max_x = d3.max(data, function(d) { return d.x })

  var canvas = d3.select("#complexity").append("svg:svg")
      .attr("width", w + m[1] + m[3])
      .attr("height", h + m [0] + m[2]);


   var group = canvas.append("svg:g")
        .attr("transform", "translate(" + m[3] + "," + m[0] + ")");


    var x = d3.scale.linear().domain([0, max_x]).range([0, w]);
    var y = d3.scale.linear().domain([0, 100]).range([h, 0]);


     var area = d3.svg.area()
        .x(function(d) {return x(d.x) ;})
        .y(function(d) {return y(d.y) ; })
        .interpolate("basis");

        


     var startData = data.map( function( d ) {
                return {
                  x  : d.x,
                  y : 0
                };
              } );

    var path = group.append("path")
      .attr("class", "path")
      .attr("d", area(data))
      .attr("stroke", color)
      .attr("fill", color);

    path
      .transition()
      .duration(500)
      .attrTween( 'd', function() {

         var interpolator = d3.interpolateArray( startData, data );

        // function called several times
        // with values from 0.0 to 1.0
        return function( t ) {
          // calculate needed values to
          // represent 'area' path with interpolated Array
          //
          // return it to set it directly to attribute 'd'
          return area( interpolator( t ) );
        }

      });

    // create yAxis
    var xAxis = d3.svg.axis().scale(x).ticks(10).orient("bottom");
    // Add the x-axis.
    group.append("svg:g")
          .attr("class", "x axis")
          .attr("transform", "translate("+  0 +   "," + (h) +")")
          .call(xAxis);


    // create left yAxis
    var yAxisLeft = d3.svg.axis().scale(y).ticks(4).orient("left");
    // Add the y-axis to the left
    group.append("svg:g")
          .attr("class", "y axis")
          .attr("transform", "translate(" + 0 + "," + ( 0 ) + ")")
          .call(yAxisLeft);

});