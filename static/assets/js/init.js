require([
    "jquery",
    "bootstrap",
    "modules/add_result",
    "modules/team_charts",
    "modules/score_chart"
], function($, Bootstrap, AddResult, TeamChart, ScoreChart) {
    $(function() {
        AddResult.init();
        TeamChart.drawChart();
        ScoreChart.drawChart($('#score-chart-container'));


        $(ScoreChart.modeSelector).on('change', function() {
            ScoreChart.drawChart($('#score-chart-container'));
        })
    });
});
