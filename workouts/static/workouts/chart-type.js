/**
 * Гистограмма по типам тренировок
 * Использует Chart.js для отображения столбчатой диаграммы
 */

document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('typeChart');
    
    if (!ctx) {
        console.warn('Элемент typeChart не найден');
        return;
    }

    new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: ['Бег', 'Силовая', 'Плавание', 'Велосипед'],
            datasets: [{
                data: [17, 12, 8, 11],
                backgroundColor: (context) => {
                    const ctx = context.chart.ctx;
                    const gradient = ctx.createLinearGradient(0, 0, 0, ctx.canvas.height);
                    
                    gradient.addColorStop(0, 'rgba(28, 103, 254, 0.65)'); // верх
                    gradient.addColorStop(1, 'rgba(28, 103, 254, 0.0)'); // низ
                    
                    return gradient;
                },
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: '',
                        color: 'var(--text-primary)'
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '',
                        color: 'var(--text-primary)'
                    },
                    grid: {
                        color: '#ECECEC'
                    }
                }
            }
        }
    });
});

