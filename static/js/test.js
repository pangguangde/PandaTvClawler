(function (H) {
    function symbolWrap(proceed, symbol, x, y, w, h, options) {
        if (symbol.indexOf('text:') === 0) {
            var text = symbol.split(':')[1],
                svgElem = this.text(text, x, y)
            .attr({
                translateY: h,
                translateX: -1
            })
            .css({
                fontFamily: 'FontAwesome',
                fontSize: h * 2
            });
            if (svgElem.renderer.isVML) {
                svgElem.fillSetter = function (value, key, element) {
                    element.style.color = H.Color(value).get('rgb');
                };
            }
            return svgElem;
        }
        return proceed.apply(this, [].slice.call(arguments, 1));
    }
    H.wrap(H.SVGRenderer.prototype, 'symbol', symbolWrap);
    if (H.VMLRenderer) {
        H.wrap(H.VMLRenderer.prototype, 'symbol', symbolWrap);
    }
    // Load the font for SVG files also
    H.wrap(H.Chart.prototype, 'getSVG', function (proceed) {
        var svg = proceed.call(this);
        svg = '<?xml-stylesheet type="text/css" ' +
            'href="http://netdna.bootstrapcdn.com/font-awesome/4.1.0/css/font-awesome.min.css" ?>' +
            svg;
        return svg;
    });
}(Highcharts));
$('#container').highcharts({
    chart: {
        type: 'scatter'
    },
    title: {
        text: '自定义数据点图标'
    },
    subtitle: {
        text: '使用 Font Awesome 图标的散点图'
    },
    yAxis: {
        title: {
            text: '体重（kg）'
        }
    },
    xAxis: {
        title: {
            text: '身高（cm）',
            y: 20,
            x: -30,
            offset: 0,
            align: 'low'
        }
    },
    tooltip: {
        shared: true,
        pointFormat: '<span style="color:{series.color}; font-family: FontAwesome">{series.options.icon}</span> {series.name}: <b>[{point.x}, {point.y}]</b><br/>'
    },
    plotOptions: {
        scatter: {
            marker: {
                states: {
                    hover: {
                        enabled: false,
                        lineWidth: 0
                    }
                }
            }
        },
        series: {
            cursor: 'default'
        }
    },
    series: [{
        data: [[174.0, 65.6], [175.3, 71.8], [193.5, 80.7], [186.5, 72.6], [187.2, 78.8],
               [181.5, 74.8], [184.0, 86.4], [184.5, 78.4], [175.0, 62.0], [184.0, 81.6],
               [180.0, 76.6], [177.8, 83.6], [192.0, 90.0], [176.0, 74.6], [174.0, 71.0],
               [184.0, 79.6], [192.7, 93.8], [171.5, 70.0], [173.0, 72.4], [176.0, 85.9],
               [176.0, 78.8], [180.5, 77.8], [172.7, 66.2], [176.0, 86.4], [173.5, 81.8],
               [178.0, 89.6], [180.3, 82.8], [180.3, 76.4], [164.5, 63.2], [173.0, 60.9]] ,
        marker: {
            symbol: 'text:\uf183' // fa-male
        },
        icon: '\uf183',
        name: '男性',
        color: 'rgba(119, 152, 191, 0.6)'
    }, {
        data: [[161.2, 51.6], [167.5, 59.0], [159.5, 49.2], [157.0, 63.0], [155.8, 53.6],
               [170.0, 59.0], [159.1, 47.6], [166.0, 69.8], [176.2, 66.8], [160.2, 75.2],
               [172.5, 55.2], [170.9, 54.2], [172.9, 62.5], [153.4, 42.0], [160.0, 50.0],
               [147.2, 49.8], [168.2, 49.2], [175.0, 73.2], [157.0, 47.8], [167.6, 68.8],
               [159.5, 50.6], [175.0, 82.5], [166.8, 57.2], [176.5, 87.8], [170.2, 72.8],
               [174.0, 54.5], [173.0, 59.8], [179.9, 67.3], [170.5, 67.8], [160.0, 47.0],
               [154.4, 46.2], [162.0, 55.0], [176.5, 83.0], [160.0, 54.4], [152.0, 45.8]],
        marker: {
            symbol: 'text:\uf182' // fa-female
        },
        icon: '\uf182',
        name: '女性',
        color: 'rgba(223, 83, 83, 0.6)'
    }]
});