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


  var w_topics = 150;
  var h_topics = 300;
  var topics_canvas = d3.select("#text").append("svg")
   .attr("width", h_topics)
    .attr("height", h_topics)
    .append("g")

    g_topics = topics_canvas
            .attr("transform", "translate(" + w_topics / 2 + "," + w_topics / 2 + ")");

    g_labels = g_topics.append("g")

  var arc = d3.svg.arc()
    .outerRadius( 60 )
    .innerRadius(50);

  var pie = d3.layout.pie()
      // .sort(null)
      .value(function(d) { return d.value; });


  var div2 = d3.select("#text").append("div")   
    //.attr("class", "tooltip")               
  var dat = d3.select("div2")
    .append("div")   
    .attr("class", "text_show")               
    .style("opacity", 0);

  var opacityscale = d3.scale.linear().domain([0.85, 1]).range([0.01, .25]);

  var layer1 = vis.append('g');
  var layer2 = vis.append('g');

  var force = self.force = d3.layout.force()
          .nodes(json["nodes"])
          .links(json["links"] )
          .gravity(.035)
          .friction(0.1)
          .distance(80)
          .charge(-300)
          .size([w_graph, h_graph])
          .start();

      var link = layer1.selectAll("line.link")
          .data(json.links)
          .enter().append("svg:line")
          .attr("class", "link")
          .style("stroke", "#555555")
          .style("stroke-opacity",0.5 )
          .style("stroke-width", function(d) { return 10 * opacityscale(d.value) })
          .attr("x1", function(d) { return d.source.x; })
          .attr("y1", function(d) { return d.source.y; })
          .attr("x2", function(d) { return d.target.x; })
          .attr("y2", function(d) { return d.target.y; });

      force.linkStrength(function(link) {
       return 0.2 + 0.8 * ( 1 - link.value );
    });


      var drag_on = false;
      var node_drag = d3.behavior.drag()
          .on("dragstart", dragstart)
          .on("drag", dragmove)
          .on("dragend", dragend);


      function dragstart(d, i) {
          drag_on = true;
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
          drag_on = false;
          d.fixed = false; //change to true to fix when moved
          tick();
          force.resume();
      }


      var current_node = null;

      var node = layer2.selectAll("g.node")
          .data(json.nodes)
        .enter().append("svg:g")
          .attr("class", "node")
          .call(node_drag);

      node.append("svg:circle")
          .attr("r" , function(d) { return d.size })
          .attr("fill" , function(d) { return d.color })
          .style("stroke", "white")
          .style("fill-opacity", 1)
          .attr("stroke", function(d) { return d.color })
          .on("mouseover", function(d) {  

            if (current_node)
            {
              current_node
              .transition()        
              .duration(300) 
              .attr("r" , function(d) { return d.size;  })
              .attr("fill", function(d) { return d.color; });

            }
            current_node = d3.select(this);

            mouseOverFunction(d) ;

            d3.select(this)
            //.style("fill", "#1abc9c")
            .transition()        
                .duration(450) 
                .ease('elastic')
                .attr("r" , function(d) { return d.size * 2  })
                .attr("fill", "#E48681");

            div.transition()        
                .duration(300)      
                .style("opacity", 1);      

            div.html(d.name)  
                .style("left", (d3.event.pageX) + "px")     
                .style("top", (d3.event.pageY - 50) + "px");


            //retrieve topics from db
            d3.json("/getTopics/"+d.name , function(e, dd_topics) {
		
            //chart
            var path = g_topics.selectAll('path')
            .data(pie(dd_topics['topics']));

            path.attr("class", "update")

            path.enter().append('path')
              .attr("class", "enter")
              .attr('d', arc)
              .attr('fill', function(d,i){ return d.data['color'];} ); 

            //update
            var id_tmp = 0
            path
              .attr('fill', function(d,i){ return d.data['color'];} )
              // .transition()
              .attr('d', arc)
              // .attrTween('d', arcTween )

            function arcTween(a) {
              var i = d3.interpolate(this._current, a);
              this._current = i(0);
              return function(t) {
              return arc(i(t));
              };
            }


            path.exit().remove() 

                // legend - (poorly coded )
            g_labels.selectAll("*").remove();
            for (var i = 0; i < dd_topics['topics'].length; i++)
            {
                g_labels.append('text')
                .attr( 'transform' , "translate( -70, "  + ( w_topics/2 +10+ i * 15 )+ ")" )
                .text( dd_topics['topics'][i]['name'])
                .style( "font-family" , "Open Sans")
                .style( "fill",  dd_topics['topics'][i]['color'])

            }
          });

              d3.json( "/getText/"+d.name , function(error, dd) {
                  div2.transition()        
                  .duration(300)      
                  .style("opacity", 1);
                  div2 .html( dd.text) ;
              })

            /*dat.append('foreignObject')
              .html( 'kdjvsjdqffqf'

                d3.json("/getTopics/"+d.name , function(error, dd) {
                  console.log(dd);
                return dd;
              })
                +
                " <br> <br>"
                +
                d3.json("/getText/"+d.name , function(error, dd) {
                return dd
              })

                )
              .select('div2')
              .transition()        
              .duration(300)      
              .style("opacity", .9);*/


            })                  
          .on("mouseout", function(d) {    

            if (!drag_on)
            {
              mouseOutFunction(d);

                div.transition()        
                    .duration(333)      
                    .style("opacity", 0);

                /*div2.transition()        
                    .duration(333)      
                    .style("opacity", 0);*/
                dat.transition()        
                    .duration(33)      
                    .style("opacity", 0);
              }
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




      // tests 



    // function (highlith neighbors)
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
