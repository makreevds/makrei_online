// Получаем данные о весе из шаблона
const weightDataJson = document.getElementById('weight-data-json');
let weightData = [];

if (weightDataJson) {
    try {
        weightData = JSON.parse(weightDataJson.textContent);
    } catch (e) {
        console.error('Ошибка парсинга данных о весе:', e);
        weightData = [];
    }
}

// Функция преобразования данных для графика
function prepareWeightChartData(data) {
    if (!data || data.length === 0) {
        // Если данных нет, возвращаем пустой массив
        return {
            dataPoints: []
        };
    }
    
    // Сортируем по дате на всякий случай
    const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));
    
    // Используем реальные даты вместо индексов
    return {
        dataPoints: sortedData.map((item) => ({
            x: item.date, // Используем ISO строку даты (YYYY-MM-DD)
            y: item.weight
        }))
    };
}

const chartData = prepareWeightChartData(weightData);

// Плагин для градиентной заливки
const curvedFillPlugin = {
    id: 'curvedFill',
    beforeDatasetDraw(chart, args) {
        const meta = chart.getDatasetMeta(args.index);
        const { ctx, chartArea } = chart;
        if (!meta || !meta.dataset || !meta.data.length) return;

        ctx.save();
        ctx.beginPath();
        meta.dataset.path(ctx);

        const first = meta.data[0];
        const last = meta.data[meta.data.length - 1];
        ctx.lineTo(last.x, chartArea.bottom);
        ctx.lineTo(first.x, chartArea.bottom);
        ctx.closePath();

        const topY = Math.min(...meta.data.map(p => p.y));
        const gradient = ctx.createLinearGradient(0, topY, 0, chartArea.bottom);
        gradient.addColorStop(0, 'rgba(156, 35, 252, 0.25)');
        gradient.addColorStop(1, 'rgba(156, 35, 252, 0)');

        ctx.fillStyle = gradient;
        ctx.fill();
        ctx.restore();
    }
};

const verticalLinePlugin = {
    id: 'verticalLine',
    afterDraw: (chart) => {
        if (!chart.tooltip._active || chart.tooltip._active.length === 0) return;

        const ctx = chart.ctx;
        const activePoint = chart.tooltip._active[0];
        const x = activePoint.element.x;

        ctx.save();
        ctx.beginPath();
        ctx.moveTo(x, chart.chartArea.top);
        ctx.lineTo(x, chart.chartArea.bottom);
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(156, 35, 252, 0.4)';
        ctx.stroke();
        ctx.restore();
    }
};

// Конфиг графика
const config = {
    type: 'line',
    data: {
        datasets: [{
            data: chartData.dataPoints,
            borderColor: accent3,
            borderWidth: 2,
            tension: 0.38,
            cubicInterpolationMode: 'monotone',
            fill: false,
            pointRadius: 3,
            pointHoverRadius: 5,
            pointBackgroundColor: accent3,
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2
        }]
    },
    options: {
        animations: {
            x: { duration: 1000, easing: 'easeInQuad' },
            y: { duration: 1000, easing: 'easeInQuad' }
        },
        plugins: {
            tooltip: {
                enabled: true,
                mode: 'nearest',
                intersect: false,
                callbacks: {
                    title: function(context) {
                        // Форматируем дату для тултипа
                        const date = new Date(context[0].parsed.x);
                        const day = String(date.getDate()).padStart(2, '0');
                        const month = String(date.getMonth() + 1).padStart(2, '0');
                        const year = date.getFullYear();
                        return `${day}.${month}.${year}`;
                    },
                    label: function(context) {
                        const point = context.raw;
                        return `Вес: ${point.y.toFixed(2)} кг`;
                    }
                }
            },
            legend: { display: false }
        },
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'day',
                    displayFormats: {
                        day: 'dd.MM.yyyy'
                    },
                    tooltipFormat: 'dd.MM.yyyy',
                    parser: 'yyyy-MM-dd' // Формат входных данных
                },
                grid: { display: false },
                ticks: {
                    maxRotation: 45,
                    minRotation: 45,
                    source: 'auto' // Автоматически выбирает подходящие даты для отображения
                }
            },
            y: {
                beginAtZero: false,
                title: {
                    display: true,
                    text: 'Вес (кг)',
                    color: textPrimary
                },
                grid: { color: '#ECECEC' },
                ticks: {
                    callback: function(value) {
                        return value.toFixed(1) + ' кг';
                    }
                },
                // Автоматически определяем диапазон, если есть данные
                ...(chartData.dataPoints.length > 0 ? {
                    suggestedMin: Math.min(...chartData.dataPoints.map(d => d.y)) - 2,
                    suggestedMax: Math.max(...chartData.dataPoints.map(d => d.y)) + 2
                } : {})
            }
        },
        interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
        }
    },
    plugins: [curvedFillPlugin, verticalLinePlugin]
};

// Создание графика
const canvas = document.getElementById('durationChart');
if (canvas) {
    const myChart = new Chart(canvas, config);
}
