var options1 = {
    series: [{
        data: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9, 54]
    }],
    chart: {
        type: "line",
        width: 120,
        height: 35,
        sparkline: {
            enabled: !0
        },
        dropShadow: {
            enabled: !0,
            top: 4,
            left: 0,
            bottom: 0,
            right: 0,
            blur: 2,
            color: "rgba(132, 145, 183, 0.3)",
            opacity: .35
        }
    },
    colors: ["#95a0c5"],
    stroke: {
        show: !0,
        curve: "smooth",
        width: [3],
        lineCap: "round"
    },
    tooltip: {
        fixed: {
            enabled: !1
        },
        x: {
            show: !1
        },
        y: {
            title: {
                formatter: function (o) {
                    return ""
                }
            }
        },
        marker: {
            show: !1
        }
    }
}
    , chart1 = new ApexCharts(document.querySelector("#line-1"), options1)
    , options2 = (chart1.render(),
    {
        series: [{
            data: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9, 54]
        }],
        chart: {
            type: "line",
            width: 120,
            height: 35,
            sparkline: {
                enabled: !0
            },
            dropShadow: {
                enabled: !0,
                top: 4,
                left: 0,
                bottom: 0,
                right: 0,
                blur: 2,
                color: "rgba(132, 145, 183, 0.3)",
                opacity: .35
            }
        },
        colors: ["#95a0c5"],
        stroke: {
            show: !0,
            curve: "smooth",
            width: [3],
            lineCap: "round"
        },
        tooltip: {
            fixed: {
                enabled: !1
            },
            x: {
                show: !1
            },
            y: {
                title: {
                    formatter: function (o) {
                        return ""
                    }
                }
            },
            marker: {
                show: !1
            }
        }
    })
    , chart2 = new ApexCharts(document.querySelector("#line-2"), options2)
    , colors = (chart2.render(),
        ["#95a0c5", "#95a0c5", "#95a0c5", "#22c55e", "#22C55E", "#95a0c5", "#95a0c5", "#95a0c5", "#95a0c5", "#95a0c5", "#95a0c5", "#95a0c5", "#22C55E"])
    , options = {
        chart: {
            height: 270,
            type: "bar",
            toolbar: {
                show: !1
            },
            dropShadow: {
                enabled: !0,
                top: 0,
                left: 5,
                bottom: 5,
                right: 0,
                blur: 5,
                color: "#45404a2e",
                opacity: .35
            }
        },
        colors: colors,
        plotOptions: {
            bar: {
                borderRadius: 6,
                dataLabels: {
                    position: "top"
                },
                columnWidth: "20",
                distributed: !0
            }
        },
        dataLabels: {
            enabled: !0,
            formatter: function (o) {
                return o + "%"
            },
            offsetY: -20,
            style: {
                fontSize: "12px",
                colors: ["#8997bd"]
            }
        },
        series: [{
            name: "Inflation",
            data: [2.3, 3.1, 4, 10.1, 10.2, 3.6, 3.2, 2.3, 1.4, .8, .5, .2, .2]
        }],
        xaxis: {
            categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            position: "top",
            axisBorder: {
                show: !1
            },
            axisTicks: {
                show: !1
            },
            crosshairs: {
                fill: {
                    type: "gradient",
                    gradient: {
                        colorFrom: "#D8E3F0",
                        colorTo: "#BED1E6",
                        stops: [0, 100],
                        opacityFrom: .4,
                        opacityTo: .5
                    }
                }
            },
            tooltip: {
                enabled: !0
            }
        },
        yaxis: {
            axisBorder: {
                show: !1
            },
            axisTicks: {
                show: !1
            },
            labels: {
                show: !0,
                formatter: function (o) {
                    return "$" + o + "k"
                }
            }
        },
        grid: {
            row: {
                colors: ["transparent", "transparent"],
                opacity: .2
            },
            strokeDashArray: 2.5
        },
        legend: {
            show: !1
        }
    }
    , chart = new ApexCharts(document.querySelector("#monthly_income"), options)
    , options = (chart.render(),
    {
        series: [{
            name: "Items",
            data: [1380, 1100, 990, 880, 740, 548, 330, 200]
        }],
        chart: {
            type: "bar",
            height: 275,
            toolbar: {
                show: !1
            }
        },
        plotOptions: {
            bar: {
                borderRadius: 6,
                horizontal: !0,
                distributed: !0,
                barHeight: "85%",
                isFunnel: !0,
                isFunnel3d: !1
            }
        },
        dataLabels: {
            enabled: !0,
            formatter: function (o, e) {
                return e.w.globals.labels[e.dataPointIndex]
            },
            dropShadow: {
                enabled: !1
            },
            style: {
                colors: ["#22c55e"],
                fontWeight: 400,
                fontSize: "13px"
            }
        },
        xaxis: {
            categories: ["Mobile", "Men Fishion", "Women Fishion", "Mobile", "Health", "Sports", "Kids", "Mobile"]
        },
        colors: ["rgba(34, 197, 94, 0.45)", "rgba(34, 197, 94, 0.4)", "rgba(34, 197, 94, 0.35)", "rgba(34, 197, 94, 0.3)", "rgba(34, 197, 94, 0.25)", "rgba(34, 197, 94, 0.2)", "rgba(34, 197, 94, 0.15)", "rgba(34, 197, 94, 0.1)"],
        legend: {
            show: !1
        }
    })
    , options = ((chart = new ApexCharts(document.querySelector("#categories"), options)).render(),
    {
        chart: {
            height: 280,
            type: "donut"
        },
        plotOptions: {
            pie: {
                donut: {
                    size: "80%"
                }
            }
        },
        dataLabels: {
            enabled: !1
        },
        stroke: {
            show: !0,
            width: 2,
            colors: ["transparent"]
        },
        series: [50, 25, 25],
        legend: {
            show: !0,
            position: "bottom",
            horizontalAlign: "center",
            verticalAlign: "middle",
            floating: !1,
            fontSize: "13px",
            fontFamily: "Be Vietnam Pro, sans-serif",
            offsetX: 0,
            offsetY: 0
        },
        labels: ["Currenet", "New", "Retargeted"],
        colors: ["#22c55e", "#08b0e7", "#ffc728"],
        responsive: [{
            breakpoint: 600,
            options: {
                plotOptions: {
                    donut: {
                        customScale: .2
                    }
                },
                chart: {
                    height: 240
                },
                legend: {
                    show: !1
                }
            }
        }],
        tooltip: {
            y: {
                formatter: function (o) {
                    return o + " %"
                }
            }
        }
    });
(chart = new ApexCharts(document.querySelector("#customers"), options)).render();
