var margin = 10
var m = [margin, margin, margin, margin]; // margins
var ww = 600//document.getElementById("topics").clientWidth;
var hh = 400//document.getElementById("topics").clientHeight;
var w = ww - m[1] - m[3]; // width
var h = hh - m[0] - m[2]; // height

console.log(FILE_TITLE)


d3.json("/topics/" + FILE_TITLE, function(error, data_topics) {

  full_data = data_topics[0];

  data = full_data['values'];
  color = full_data['color'];


  var max_x = d3.max(data, function(d) { return d.x })

  var canvas = d3.select("#topics").append("svg:svg")
      .attr("width", w + m[1] + m[3])
      .attr("height", h + m [0] + m[2]);


   var group = canvas.append("svg:g")
        .attr("transform", "translate(" + m[3] + "," + m[0] + ")");


    var sx = d3.scale.linear().domain([0, max_x]).range([0, w]);
    var sy = d3.scale.linear().domain([0, 1]).range([h, 0]);


     var line = d3.svg.line()
        .x(function(d) {return sx(d.x) ;})
        .y(function(d) {return sy(d.y) ; })
        .interpolate("basis");

  var legendRectSize = 15;
  var legendSpacing = 4;

  var label_offset = w / data_topics.length;

  //draw lines and legends

  legend_y = (-2*m[0]/3) 
  for ( var i = 0; i < data_topics.length ; i++ )
  {
    col = data_topics[i]['color']
    dat = data_topics[i]['values']
    var path = group.append('path')
          .attr('d', line( data_topics[i]['values'] ))
          .data([dat])
          .attr("fill", "none")
          .attr("stroke", col)
          .attr("stroke-width", 20);


    var totalLength = path.node().getTotalLength();
    path
      .attr("stroke-dasharray", totalLength + " " + totalLength)
      .attr("stroke-dashoffset", totalLength)
      .transition()
        .duration(900)
        .ease("linear")
        .attr("stroke-dashoffset", 0);

    
    offset_x = 0
    offset_y = 0
    for ( var j = 0; j < i ; j++ )
    {
      tmp = 10
      tmp += (data_topics[j]['label']).length * 9
      offset_x += tmp
      if (offset_x > w - 20 )
      {
        console.log("############ HERE #########")
         offset_x = 0
         offset_y += 20

      }

    }
    cur_x = offset_x;
    cur_y = legend_y + offset_y; 
    //create labels
    group.append('rect')
      .attr('width', legendRectSize)
      .attr('height', legendRectSize)
      .style('fill', col)
      .style('stroke', col)
      .attr("transform", "translate(" + cur_x + "," +  cur_y + ")");

    group.append('text')
      .attr('x', cur_x + legendRectSize + legendSpacing)
      .attr('y', cur_y + legendRectSize - 4)
      .text(data_topics[i]['label']);

  }

    // create yAxis
    var xAxis = d3.svg.axis().scale(sx).ticks(5).orient("bottom");
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



d3.select(window).on('resize', resize); 

function resize() {
    // update width
    w = parseInt(d3.select('#topics').style('width'), 10);
    w = w - margin - margin;

    // resize the chart
    sx.domain([0, max_x]).range([0, w]);
    sy.domain([0, 1]).range([h, 0]);

    line.x(function(d) {return sx(d.x) ;})
        .y(function(d) {return sy(d.y) ; })
        .interpolate("basis");


    for ( var i = 0; i < data_topics.length ; i++ )
    {
      col = data_topics[i]['color']
      path.attr('d', line( data_topics[i]['values'] ))
            .data([data_topics[i]['values']])
            .attr("fill", "none")
            .attr("stroke", col)
            .attr("stroke-width", 20);
    }

}


});