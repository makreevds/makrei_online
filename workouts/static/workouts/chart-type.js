/**
 * Гистограмма по типам тренировок
 * Использует Chart.js для отображения столбчатой диаграммы
 * Данные загружаются из базы данных через JSON
 */

document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('typeChart');
    
    if (!ctx) {
        console.warn('Элемент typeChart не найден');
        return;
    }

    // Получаем данные о типах тренировок из шаблона
    const workoutTypesDataJson = document.getElementById('workout-types-data-json');
    let workoutTypesData = {
        labels: [],
        data: []
    };

    if (workoutTypesDataJson) {
        try {
            workoutTypesData = JSON.parse(workoutTypesDataJson.textContent);
        } catch (e) {
            console.error('Ошибка парсинга данных о типах тренировок:', e);
            workoutTypesData = { labels: [], data: [] };
        }
    }

    // Если нет данных, показываем пустой график
    if (!workoutTypesData.labels || workoutTypesData.labels.length === 0) {
        workoutTypesData = {
            labels: ['Нет данных'],
            data: [0]
        };
    }

    new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: workoutTypesData.labels,
            datasets: [{
                data: workoutTypesData.data,
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
            maintainAspectRatio: false,
            responsive: true,
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
                    },
                    ticks: {
                        color: 'var(--text-primary)',
                        maxRotation: 45,
                        minRotation: 0
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
                    },
                    ticks: {
                        color: 'var(--text-primary)',
                        stepSize: 1
                    }
                }
            }
        }
    });
});

