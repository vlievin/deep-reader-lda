  var w_graph = 1600;
  var h_graph = 1400;

json = []

var dat = d3.json("/network", function(error, json) {

  var vis = d3.select("body").append("svg")
    .attr("width", w_graph)
    .attr("height", h_graph);

  var div = d3.select("body").append("div")   
    .attr("class", "tooltip")               
    .style("opacity", 0);



  var force = self.force = d3.layout.force()
          .nodes(json["nodes"])
          .links(json["links"] )
          .gravity(.05)
          .distance(100)
          .charge(-100)
          .size([w_graph, h_graph])
          .start();

      var link = vis.selectAll("line.link")
          .data(json.links)
          .enter().append("svg:line")
          .attr("class", "link")
          .style("stroke", "rgba(10,10,10,0.1)")
          .attr("x1", function(d) { return d.source.x; })
          .attr("y1", function(d) { return d.source.y; })
          .attr("x2", function(d) { return d.target.x; })
          .attr("y2", function(d) { return d.target.y; });

      var node_drag = d3.behavior.drag()
          .on("dragstart", dragstart)
          .on("drag", dragmove)
          .on("dragend", dragend);

      function dragstart(d, i) {
          force.stop() // stops the force auto positioning before you start dragging
      }

      function dragmove(d, i) {
          d.px += d3.event.dx;
          d.py += d3.event.dy;
          d.x += d3.event.dx;
          d.y += d3.event.dy; 
          tick(); // this is the key to make it work together with updating both px,py,x,y on d !
      }

      function dragend(d, i) {
          d.fixed = false; //change to true to fix when moved
          tick();
          force.resume();
      }


      var node = vis.selectAll("g.node")
          .data(json.nodes)
        .enter().append("svg:g")
          .attr("class", "node")
          .call(node_drag);

      node.append("svg:circle")
          .attr("r" , function(d) { return d.size })
          .attr("fill" , function(d) { return d.color })
          .style("fill-opacity", .5)
          .attr("stroke", function(d) { return d.color })
          .on("mouseover", function(d) {   

            d3.select(this).style("fill", "#1abc9c");
            div.transition()        
                .duration(200)      
                .style("opacity", .9);      
            div .html(d.name)  
                .style("left", (d3.event.pageX) + "px")     
                .style("top", (d3.event.pageY - 50) + "px");    
            })                  
          .on("mouseout", function(d) {       
              d3.select(this).style("fill", function(d) { return d.color });
              div.transition()        
                  .duration(500)      
                  .style("opacity", 0);   
          });

      /*node.append("svg:text")
          .attr("class", "nodetext")
          .attr("dx", 8)
          .attr("dy", ".35em")
          .style("font-size","12pt")
          .text(function(d) { return d.name });*/

      force.on("tick", tick);

      function tick() {
        link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

        node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
      };

  

});