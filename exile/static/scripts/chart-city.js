var ctx = document.getElementById('chart');
new Chart(ctx, {
    type: 'pie',
    data: {
        labels: overviewChartLabels,
        datasets: [{
            data: overviewChartDataset,
            backgroundColor: [
                "#D92662",
                "#D9269D",
                "#9236A4",
                "#7540BF",
                "#524ED2",
                "#3C71F7",
                "#017FC0",
                "#058686",
                "#00895A",
                "#398712",
                "#A5D601",
                "#F2DF0D",
                "#FFBF00",
                "#FF9500",
                "#D24317",
                "#D93526",
            ],
            hoverOffset: 4
        }]
    },
    options: {
        animation: {
            duration: 0
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    precision: 0
                }
            }
        },
        resizeDelay: 600,
    }
});