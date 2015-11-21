 var w_graph = 1200;
  var h_graph = 800;
  var margin = 50;

var dat = d3.json("/similarities", function(error, data) {

  var canvas = d3.select("#closestTexts").append("svg")
    .attr("width", w_graph)
    .attr("height", h_graph);

	var xscale = d3.scale.linear()
						.domain([0,1])
						.range([margin ,w_graph - margin]);

	var yscale = d3.scale.linear()
						.domain([0,data.length])
						.range([margin,h_graph-margin]);

	var h_bar = (h_graph - 2 * margin ) / data.length - 1

	var tooltip = d3.select("body")
	.append("div")
	.attr('class', 'tip')
	.style("position", "absolute")
	.style("z-index", "10")
	.style("visibility", "hidden")
	.style("fill", "rgba(0, 0, 0, 0.5)")
	.style("box-shadow", " 0px 0px 5px gray")
	/*.text("a simple tooltip");*/

	/*canvas
	.on("mouseover", function(){return tooltip.style("visibility", "visible");})
	.on("mousemove", function(){return tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");})
	.on("mouseout", function(){return tooltip.style("visibility", "hidden");});*/

	var chart = canvas.append('g')
							.attr("transform", "translate(150,0)")
							.attr('id','bars')
							.selectAll('rect')
							.data(data)
							.enter()
							.append('rect')
							.attr('height',h_bar)
							.attr({'x':0,'y':function(d,i){ return yscale(i); }})
							.style('stroke', 'none')
							.style('fill', '#3498db')
							.attr('width',function(d){ return xscale(d.similarity); })
							.attr('transform','translate(50,50)')
							.on("mouseover", function(d){tooltip.select('.tip').html( " name:" + d.name); d3.select(this).style('fill', '#e74c3c');return tooltip.style("visibility", "visible");})
							.on("mousemove", function(){return tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");})
							.on("mouseout", function(){d3.select(this).style('fill', '#3498db');return tooltip.style("visibility", "hidden");});/*


	/*var transit = d3.select("svg").selectAll("rect")
						    .data(data)
						    .transition()
						    .duration(1000) 
						    .attr("width", function(d) {return xscale(d.similarity); })*/




});