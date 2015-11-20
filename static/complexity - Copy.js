var m = [80, 50, 80, 50]; // margins
var w = 600- m[1] - m[3]; // width
var h = 400 - m[0] - m[2]; // height

d3.json("/complexity", function(error, full_data) {

  data = full_data['values']
  color = full_data['color']

  console.log(data)
  console.log(color)


  var max_x = d3.max(data, function(d) { return d.x })

  console.log( max_x)

  var canvas = d3.select("#complexity").append("svg:svg")
      .attr("width", w + m[1] + m[3])
      .attr("height", h + m [0] + m[2]);


   var group = canvas.append("svg:g")
        .attr("transform", "translate(" + m[3] + "," + m[0] + ")");


    var sx = d3.scale.linear().domain([0, max_x]).range([0, w]);
    var sy = d3.scale.linear().domain([0, 100]).range([h, 0]);


     var line = d3.svg.line()
        .x(function(d) {return sx(d.x) ;})
        .y(function(d) {return sy(d.y) ; })
        .interpolate("basis");

    var path = group.append("path")
      .attr("d", line(data))
      .attr("stroke", color)
      .attr("stroke-width", "2")
      .attr("fill", "none");


    var totalLength = path.node().getTotalLength();

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

    /*path
      .attr("stroke-dasharray", totalLength + " " + totalLength)
      .attr("stroke-dashoffset", totalLength)
      .transition()
        .duration(900)
        .ease("linear")
        .attr("stroke-dashoffset", 0);*/

   /*group.selectAll("path")
        .data([data])
        .enter()
        .append("path")
        .attr("d", line)
        .attr("fill", "none")
        .attr("stroke", color)
        .attr("stroke-width", 20)
        .transition()
          .duration(3000)
          .ease("line")
          .attr("stroke-dashoffset", 0);*/


    // create yAxis
    var xAxis = d3.svg.axis().scale(sx).ticks(10).orient("bottom");
    // Add the x-axis.
    group.append("svg:g")
          .attr("class", "x axis")
          .attr("transform", "translate("+  0 +   "," + (h) +")")
          .call(xAxis);


    // create left yAxis
    var yAxisLeft = d3.svg.axis().scale(sy).ticks(4).orient("left");
    // Add the y-axis to the left
    group.append("svg:g")
          .attr("class", "y axis")
          .attr("transform", "translate(" + 0 + "," + ( 0 ) + ")")
          .call(yAxisLeft);

});