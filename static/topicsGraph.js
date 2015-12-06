  var w_graph = 1200;
  var h_graph = 800;

json = []

var dat = d3.json("/topicsGraph/" + FILE_TITLE, function(error, json) {

  var vis = d3.select("#topicsGraph").append("svg")
    .attr("width", w_graph)
    .attr("height", h_graph);

  var force = self.force = d3.layout.force()
          .nodes(json["nodes"])
          .links(json["links"] )
          .gravity(.05)
          .distance(80)
          .charge(-100)
          .size([w_graph, h_graph])
        //   .linkDistance( function(link) {

	      	// console.log(link.value);
	       // return   ( 1* ( link.value )); })
          .linkStrength( function(link) {

	       return   ( 0.05 *   (  0.2 + 0.8 * ( 100 - link.value ))); })
          .start();

      var link = vis.selectAll("line.link")
          .data(json.links)
          .enter().append("svg:line")
          .attr("class", "link")
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

          	 mouseOverFunction(d) ;

          })
          .on("mouseout", function(d) {    

          	mouseOutFunction(d);

          });

      node.append("svg:text")
          .attr("class", "nodetext")
          .attr("dx", 12)
          .attr("dy", ".35em")
          .style("font-size","12pt")
          .text(function(d) { return d.name });


      force.on("tick", tick);

      function tick() {
        link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

        node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
      };



      var linkedByIndex = {};
      json["links"] .forEach(function(d) {
        linkedByIndex[d.source.index + "," + d.target.index] = true;
      });

    function isConnected(a, b) {
      return isConnectedAsTarget(a, b) || isConnectedAsSource(a, b) || a.index == b.index;
    }

    function isConnectedAsSource(a, b) {
      return linkedByIndex[a.index + "," + b.index];
    }

    function isConnectedAsTarget(a, b) {
      return linkedByIndex[b.index + "," + a.index];
    }

    function isEqual(a, b) {
      return a.index == b.index;
    }


    var mouseOverFunction = function(d) {

    //var circle = d3.select(this);

      node
        .transition(500)
          .style("opacity", function(o) {
            return isConnected(o, d) ? 1.0 : 0.2 ;
          });

      link
        .transition(500)
          .style("stroke-opacity", function(o) {
            return o.source === d || o.target === d ? 0.5 : 0.1;
          })
          /*.style("stroke-width", function(o) {
            return o.source === d || o.target === d  ? 1.5 : 1;
          })*/
    }

    var mouseOutFunction = function(d) {
      var circle = d3.select(this);

      node
        .transition(500)
          .style("opacity", function(o) {
            return isConnected(o, d) ? 1 : 1 ;
          });

      
      link
        .transition(500)
          .style("stroke-opacity", function(o) {
            return o.source === d || o.target === d ? 0.5 : 0.5;
          })


    /*layer1.selectAll()
        .data(json.links)
        .enter().append("svg:line")
        .attr("class", "link")
        .style("stroke", function(d) { return "rgba(10,10,10, "+ opacityscale(d.value) + ")"})
        .style("stroke-width", function(d) { return 5 * opacityscale(d.value) });
          /*.style("stroke-width", function(o) {
            return o.source === d || o.target === d  ? 1 : 1;
          })*/
    }


    

  

});