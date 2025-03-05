function createChart(data, type) {
    const ctx = document.getElementById('statsChart').getContext('2d');
    
    new Chart(ctx, {
        type: type,
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Статистика',
                data: data.values,
                backgroundColor: [
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}