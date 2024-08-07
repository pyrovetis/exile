var ctx = document.getElementById('chart');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: overviewChartLabels,
        datasets: [{
            label: "# of Views",
            data: overviewChartDataset,
            backgroundColor: "#ffbf00",
            borderColor: "#ffbf00",
            radius: 5,
            hoverRadius: 6,
            hitRadius: 10,
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