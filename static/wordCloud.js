var frequency_list = []
d3.json("/significantWords", function(error, full_data) {

  frequency_list = full_data

  var layout = d3.layout.cloud();

  var fill = d3.scale.category20();

  font_size_factor = 1

  console.log(fill)

  var words = ["Hello", "world", "normally", "you", "want", "more", "words", "than", "this"]
      .map(function(d) {
        return {text: d, size: 10 + Math.random() * 90};
      });

  layout.size([1200, 600])
      .words(frequency_list)
      .padding(5)
      .rotate(function() { return 0; })
      .font("Impact")
      .text(function(d) { return d.text; })
      .fontSize(function(d) { return (d.size * font_size_factor*  2); })
      .on("end", draw)


  layout.start();

  function draw(words) {
    cloud = d3.select("#wordCloud").append("svg")
        .attr("width", layout.size()[0])
        .attr("height", layout.size()[1])
      .append("g")
        .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
      .selectAll("text")
        .data(words)
      .enter().append("text")
        .style("font-size", function(d) { return (0 ) + "px"; })
        .style("font-family", "Impact")
        .style("fill", function(d, i) { return d.color; })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")rotate(" +0+ ")";
        })
        .text(function(d) { return d.text; });


       cloud
      .transition()
          .duration(600)
          .style("font-size", function(d) { return (d.size * font_size_factor) + "px"; })

          .style("fill-opacity", 1);
  }

});