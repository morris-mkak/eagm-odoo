odoo.define('ks_sales_forecast.KsGraphView', function (require) {
    "use strict";
    var AbstractField = require('web.AbstractField');
    var ks_field_registry = require('web.field_registry');
    var ajax = require('web.ajax');

    var KsGraphView = AbstractField.extend({
        jsLibs: [
           '/web/static/lib/Chart/Chart.js',
        ],
        resetOnAnyFieldChange: true,
        template: 'Graph_template',
        xmlDependencies: [
            '/ks_sales_forecast/static/src/xml/ks_graph_template.xml',
        ],
        events: {
            'click #ks_line_chart': '_ks_line_chart',
            'click #ks_bar_chart': '_ks_bar_chart',
        },
        init: function (parent, value) {
            var self = this;
            this._super.apply(this,arguments);
        },

        _ks_line_chart: function(){
            this.render_Linechart();
        },

        _ks_bar_chart: function(){
            this.render_Barchart();
        },

        renderElement: function () {
            this._super();
            if(this.recordData.ks_chart_data){
                if (this.recordData.ks_is_bar_chart){
                    this.render_Barchart();
                }else{
                    this.render_Linechart();
                }
            }
        },

        render_Linechart:function(){
            this.$el.find('.ks_chart_container').empty()

            var canvas = '<canvas id="canvas" style="width: 1050px; height: 500px"></canvas>'
            this.$el.find('.ks_chart_container').append($(canvas))

            var header = "Line Chart"
            this.$el.find('.ks_header').find('.ks_header_part').text(header);

            var ctx = this.$el.find('#canvas').get(0).getContext('2d');
            var chart_data = JSON.parse(this.recordData.ks_chart_data)
            var myChart = new Chart(ctx, {
                type: 'line',
                data: chart_data,
                options: {
                    legend: {
                            display: (chart_data.datasets && chart_data.datasets.length >20) ? false : true
                       },
                }
            });
            this.ks_chart_color(myChart, 'line')
        },

        ks_chart_color: function(ksMyChart, ksChartType){
            var chartColors = [];
            var datasets = ksMyChart.config.data.datasets;
            var setsCount = datasets.length;
            var color_set = ['#F04F65', '#f69032', '#fdc233', '#53cfce', '#36a2ec', '#8a79fd', '#b1b5be', '#1c425c', '#8c2620', '#71ecef', '#0b4295', '#f2e6ce', '#1379e7']
            for (var i = 0, counter = 0; i < setsCount; i++, counter++) {
                if (counter >= color_set.length) counter = 0; // reset back to the beginning
                chartColors.push(color_set[counter]);
            }
            for (var i = 0; i < datasets.length; i++) {
                switch (ksChartType) {
                    case "line":
                        datasets[i].borderColor = chartColors[i];
                        datasets[i].backgroundColor = "rgba(255,255,255,0)";
                        break;
                    case "bar":
                        datasets[i].backgroundColor = chartColors[i];
                        datasets[i].borderColor = "rgba(255,255,255,0)";
                        break;
                }
            }
            ksMyChart.update();
        },

        render_Barchart:function(){
            this.$el.find('.ks_chart_container').empty()

            var canvas = '<canvas id="canvas" style="width: 1050px; height: 500px"></canvas>'
            this.$el.find('.ks_chart_container').append($(canvas))

            var header = "Bar Chart"
            this.$el.find('.ks_header').find('.ks_header_part').text(header);

            var ctx = this.$el.find('#canvas').get(0).getContext('2d');
            var chart_data = JSON.parse(this.recordData.ks_chart_data)
            var myChart = new Chart(ctx, {
                type: 'bar',
                data: chart_data,
                options: {
                    legend: {
                            display: (chart_data.datasets && chart_data.datasets.length >20) ? false : true
                       },
                }
            });
            this.ks_chart_color(myChart, 'bar')
        },
    });

    ks_field_registry.add('ks_graph', KsGraphView);

    return KsGraphView;

});