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

  var div = d3.select("body").append("div")   
    .attr("class", "tooltip")               
    .style("opacity", 0);

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
							.on("mouseover", function(d){
								
								d3.select(this).style('fill', '#e74c3c');
								div.transition()        
					                .duration(300)      
					                .style("opacity", 1);      

					            div.html(d.name)  
					                .style("left", (d3.event.pageX) + "px")     
					                .style("top", (d3.event.pageY - 50) + "px");
							})
							.on("mousemove", function(){
								return tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");
							})
							.on("mouseout", function(){
							d3.select(this).style('fill', '#3498db');

							div.transition()        
			                  .duration(333)      
			                  .style("opacity", 0);
							
							});/*


	/*var transit = d3.select("svg").selectAll("rect")
						    .data(data)
						    .transition()
						    .duration(1000) 
						    .attr("width", function(d) {return xscale(d.similarity); })*/




});