function drawAuthorChart() {

  var width = 300, //960,
      height = 250,
      radius = Math.min(width, height) / 2;

  var color = d3.scale.category20();

  // create the pie chart
  
  var arc = d3.svg.arc()
      .outerRadius(radius - 10)
      .innerRadius(radius - 70);

  var pie = d3.layout.pie()
      .value(function(d) { return d.urls; });

  var svg = d3.select("#author-chart").append("svg")
      .attr("id", "pie")
      .attr("width", width)
      .attr("height", height)
    .append("g")
      .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

  // fetch the data
  
  d3.csv("authors.csv", function(error, data) {

    // add data as pie chart wedges
    
    var g = svg.selectAll(".arc")
        .data(pie(data))
      .enter().append("g")
        .attr("class", "arc");

    g.append("path")
        .attr("d", arc)
        .style("fill", function(d) { return color(d.data.name); });

    // create the legend

    var legend = d3.select("#author-chart").append("svg")
        .attr("id", "legend")
        .attr("width", 210)
        .attr("height", 250)
      .selectAll("g")
        .data(data)
      .enter().append("g")
        .attr("transform", function(d, i) {
          return "translate(0," + i * 20 + ")"; });

    legend.append("rect")
        .attr("width", 18)
        .attr("height", 18)
        .style("fill", function(d) { return color(d.name); });

    legend.append("text")
        .attr("x", 24)
        .attr("y", 9)
        .attr("dy", ".35em")
        .attr("class", "legend-text")
        .attr("id", function(d) { return "legend-text-" + d.id; })
        .text(function(d) { return d.name; })
        .on("click", function(d) { 
          window.location.href = "/author/" + d.id;
        })
        .on("mouseover", function(d) {
          d3.select("#legend-text-" + d.id)
            .attr("fill", "blue");
        })
        .on("mouseout", function(d) {
          d3.select("#legend-text-" + d.id)
            .attr("fill", "black");
        });

    // add number of urls to the chart wedges
    
    g.append("text")
        .attr("transform", function(d) { 
          return "translate(" + arc.centroid(d) + ")"; 
        })
        .attr("dy", ".35em")
        .style("text-anchor", "middle")
        .text(function(d) { return d.data.urls; });

  });

}
