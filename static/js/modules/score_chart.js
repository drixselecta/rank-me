define(["jquery", "underscore", "d3"], function($, _, d3) {
    var ScoreChart = function () {
        var modeSelector = 'input[name="score-chart-mode"]';
        var buttonSelector = '.move-chart';

        var offset = 0;

        var svg;
        var line;
        var attribute;
        var positions;
        var x, y;
        var yAxis;

        function setDomain(event) {
            x.domain([1, positions[0].values.length]);

            var bigger = d3.max(positions, function(p) { return d3.max(p.values, function(v) { return v[attribute]; })});
            var smaller = d3.min(positions, function(p) { return d3.min(p.values, function(v) { return v[attribute]; })});

            var start = smaller;
            var end = bigger;

            if(attribute !== 'position') {
                start = bigger;
                end = smaller;
            }

            if(event) {
                // set the domain a first time so that we can compute the domain center
                y.domain([start, end]);

                var center = Math.max(event.sourceEvent.pageY - $(svg[0]).parent().offset().top, 0);
                var domainCenter = Math.max(Math.min(y.invert(center), bigger), smaller);

                start = domainCenter + ((start - domainCenter) * event.scale);
                end = domainCenter + ((end - domainCenter) * event.scale);
            }

            y.domain([start, end]);
        }

        function redraw() {
            var event = null;
            var duration = 1250;

            if(d3.event && d3.event.type == 'zoom') {
                event = d3.event;
                duration = 100;
            }

            var t = svg.selectAll(".position").transition().duration(duration);

            setDomain(event);

            // redraw relevent part of each item
            t.select('path')
                .attr('d', function(d) { return line(d.values); });

            t.selectAll('circle')
                .attr("transform", function(d, idx) { return "translate(" + x(idx + 1) + "," + y(d[attribute]) + ")"; });

            svg.select('.y.axis').call(yAxis);
        }

        function drawChart(container) {
            if(container.length == 0) {
                return;
            }

            $(buttonSelector).on('click', function () {
                offset += $(this).data('movement');
                offset = Math.max(offset, 0);
                doDraw(container);
            });

            $(modeSelector).on('change', function() {
                attribute = $(this).val();
                redraw();
            });

            doDraw(container);
        }

        function doDraw(container) {
            var url = container.data('json') + '/' + offset;
            d3.json(url, function(err, data) {
                if(err) {
                    alert(err);
                    return;
                }

                var margin = { top: 20, right: 150, bottom: 10, left: 40 };
                var width = container.width() - margin.left - margin.right;
                var height = 400;

                attribute = $(modeSelector + ':checked').val();
                var color = d3.scale.category20();

                x = d3.scale.linear()
                    .range([0, width]);
                y = d3.scale.linear()
                    .range([0, height]);

                line = d3.svg.line()
                    .interpolate("linear")
                    .x(function(d, idx) { return x(idx + 1); })
                    .y(function(d) { return y(d[attribute]); });

                var zoom = d3.behavior.zoom()
                    .scaleExtent([0.1, 1])
                    .on("zoom", redraw);

                container.empty();
                svg = d3.select(container[0])
                    .append('svg')
                    .attr('width', width + margin.left + margin.right)
                    .attr('height', height + margin.top + margin.bottom)
                    .call(zoom)
                    .style("pointer-events", "all")
                  .append('g')
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

                color.domain(d3.keys(data));

                for(var name in data) {
                    if(data.hasOwnProperty(name)) {
                        data[name].map(function(d) {
                            d.name = name;
                            return d;
                        });
                    }
                }

                positions = color.domain().map(function(name) {
                    return {
                        name: name,
                        values: data[name]
                    };
                });

                if(positions.length === 0) {
                    svg.append('text').text('No games to display !');
                    return;
                }

                setDomain();

                var position = svg.selectAll('.position')
                    .data(positions)
                  .enter()
                    .append('g')
                    .attr('class', 'position');

                position.append('path')
                    .attr('d', function(d) { return line(d.values); })
                    .attr('class', 'line')
                    .style("stroke", function (d) { return color(d.name); })
                    .call(highlighter);

                position.selectAll('circle')
                    .data(function(d) { return d.values; })
                  .enter()
                    .append('circle')
                    .attr('r', function(d) { return d.played ? 5 : 0; })
                    .style('fill', function(d) { return d.win ? color(d.name) : 'white'; })
                    .style('stroke', function(d) { return color(d.name); })
                    .attr("transform", function(d, idx) { return "translate(" + x(idx + 1) + "," + y(d[attribute]) + ")"; })
                    .call(highlighter);

                var itemNumber = data[Object.keys(data)[0]].length;

                position.append("text")
                    .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
                    .attr("transform", function(d) { return "translate(" + x(itemNumber) + "," + y(d.value[attribute]) + ")"; })
                    .attr("x", 10)
                    .attr("dy", ".35em")
                    .style('fill', function(d) { return color(d.name); })
                    .text(function(d) { return d.name; })
                    .call(highlighter);

                yAxis = d3.svg.axis()
                    .scale(y)
                    .ticks(20)
                    .tickSize(0)
                    .orient('left');

                svg.append("g")
                    .attr("class", "y axis")
                    .attr("transform", function(d, idx) { return "translate(-5, 0)"; })
                    .call(yAxis);

            });
        }

        function highlighter(elems) {
            elems.each(function() {
                d3.select(this)
                    .attr('class', function(d) { return 'player-' + d.name; })
                    .on('mouseover', highlight)
                    .on('mouseout', unhighlight)
                  .append('title')
                    .text(function(d) {
                        if(d.value) {
                            d = d.value;
                        } else if(d.values) {
                            d = d.values[d.values.length - 1];
                        }
                        return 'Skill : ' + (Math.round(d.skill * 100) / 100) + '\r\nPosition : ' + d.position;
                    })
            });
        }

        function highlight(d) {
            var c = 'player-' + d.name;
            d3.selectAll('.' + c).attr('class', 'highlighted ' + c);
        }

        function unhighlight(d) {
            var c = 'player-' + d.name;
            d3.selectAll('.' + c).attr('class', c);
        }

        return {
            modeSelector: modeSelector,
            drawChart: drawChart
        };
    }();

    return ScoreChart;
});
