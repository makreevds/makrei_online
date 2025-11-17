(function() {
    'use strict';
    
    // Создаем canvas для фона
    var canvas = document.createElement("canvas");
    canvas.id = "metaballs-canvas";
    canvas.style.position = "fixed";
    canvas.style.top = "0";
    canvas.style.left = "0";
    canvas.style.width = "100%";
    canvas.style.height = "100%";
    canvas.style.zIndex = "-1";
    canvas.style.pointerEvents = "none";
    
    var width = canvas.width = window.innerWidth;
    var height = canvas.height = window.innerHeight;
    
    document.body.appendChild(canvas);
    
    var gl = canvas.getContext('webgl');
    if (!gl) {
        console.warn('WebGL не поддерживается, эффект метаболов не будет отображаться');
        return;
    }
    
    var mouse = {x: 0, y: 0};
    
    // Читаем цвета из CSS переменных
    var rootStyles = getComputedStyle(document.documentElement);
    var metaballColorR = parseFloat(rootStyles.getPropertyValue('--metaball-color-r').trim()) / 255.0;
    var metaballColorG = parseFloat(rootStyles.getPropertyValue('--metaball-color-g').trim()) / 255.0;
    var metaballColorB = parseFloat(rootStyles.getPropertyValue('--metaball-color-b').trim()) / 255.0;
    var metaballMixR = parseFloat(rootStyles.getPropertyValue('--metaball-mix-color-r').trim()) / 255.0;
    var metaballMixG = parseFloat(rootStyles.getPropertyValue('--metaball-mix-color-g').trim()) / 255.0;
    var metaballMixB = parseFloat(rootStyles.getPropertyValue('--metaball-mix-color-b').trim()) / 255.0;
    var metaballOpacity = parseFloat(rootStyles.getPropertyValue('--metaball-opacity').trim());
    
    // Адаптивные параметры в зависимости от размера экрана
    function getAdaptiveParams() {
        var screenWidth = window.innerWidth;
        var screenHeight = window.innerHeight;
        var screenArea = screenWidth * screenHeight;
        
        // Количество метаболов: меньше на маленьких экранах
        // Базовое количество рассчитывается от площади экрана
        var baseNumMetaballs = Math.floor(screenArea / 50000); // примерно 1 метабол на 50000 пикселей
        var numMetaballs = Math.max(8, Math.min(30, baseNumMetaballs)); // минимум 8, максимум 30
        
        // Размер метаболов: меньше на маленьких экранах
        var minRadius = screenWidth < 768 ? 40 : 60; // на мобильных меньше
        var maxRadius = screenWidth < 768 ? 40 : 60; // на мобильных меньше
        // radiusMultiplier определяет коэффициент, на который умножается радиус каждого метабола.
        // Здесь это всегда 1.2 и для мобильных (<768px), и для остальных экранов —
        // то есть радиус фактически увеличивается на 20% по сравнению с базовым вычисленным.
        var radiusMultiplier = 1.2;
        
        // Скорость движения: медленнее на маленьких экранах
        var speedMultiplier = screenWidth < 768 ? 1.2 : 2.0;
        
        return {
            numMetaballs: numMetaballs,
            minRadius: minRadius,
            maxRadius: maxRadius,
            radiusMultiplier: radiusMultiplier,
            speedMultiplier: speedMultiplier
        };
    }
    
    var params = getAdaptiveParams();
    var numMetaballs = params.numMetaballs;
    var metaballs = [];
    
    for (var i = 0; i < numMetaballs; i++) {
        var radius = Math.random() * (params.maxRadius - params.minRadius) + params.minRadius;
        metaballs.push({
            x: Math.random() * (width - 2 * radius) + radius,
            y: Math.random() * (height - 2 * radius) + radius,
            vx: (Math.random() - 0.5) * params.speedMultiplier,
            vy: (Math.random() - 0.5) * params.speedMultiplier,
            r: radius * params.radiusMultiplier
        });
    }
    
    var vertexShaderSrc = `
        attribute vec2 position;
        
        void main() {
            gl_Position = vec4(position, 0.0, 1.0);
        }
    `;
    
    var fragmentShaderSrc = `
        precision highp float;
        
        const float WIDTH = ` + (width >> 0) + `.0;
        const float HEIGHT = ` + (height >> 0) + `.0;
        
        uniform vec3 metaballs[` + numMetaballs + `];
        
        void main(){
            float x = gl_FragCoord.x;
            float y = gl_FragCoord.y;
            
            float sum = 0.0;
            for (int i = 0; i < ` + numMetaballs + `; i++) {
                vec3 metaball = metaballs[i];
                float dx = metaball.x - x;
                float dy = metaball.y - y;
                float radius = metaball.z;
                
                sum += (radius * radius) / (dx * dx + dy * dy);
            }
            
            if (sum >= 0.99) {
                vec3 color1 = vec3(` + metaballColorR + `, ` + metaballColorG + `, ` + metaballColorB + `);
                vec3 color2 = vec3(` + metaballMixR + `, ` + metaballMixG + `, ` + metaballMixB + `);
                gl_FragColor = vec4(mix(color1, color2, max(0.0, 1.0 - (sum - 0.99) * 100.0)), ` + metaballOpacity + `);
                return;
            }
            
            gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
        }
    `;
    
    var vertexShader = compileShader(vertexShaderSrc, gl.VERTEX_SHADER);
    var fragmentShader = compileShader(fragmentShaderSrc, gl.FRAGMENT_SHADER);
    
    var program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    gl.useProgram(program);
    
    var vertexData = new Float32Array([
        -1.0,  1.0,
        -1.0, -1.0,
         1.0,  1.0,
         1.0, -1.0,
    ]);
    var vertexDataBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, vertexDataBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertexData, gl.STATIC_DRAW);
    
    var positionHandle = getAttribLocation(program, 'position');
    gl.enableVertexAttribArray(positionHandle);
    gl.vertexAttribPointer(positionHandle, 2, gl.FLOAT, gl.FALSE, 2 * 4, 0);
    
    var metaballsHandle = getUniformLocation(program, 'metaballs');
    
    // Обработка изменения размера окна
    function handleResize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
        gl.viewport(0, 0, width, height);
        
        // Обновляем позиции метаболов, если они вышли за границы
        var newParams = getAdaptiveParams();
        for (var i = 0; i < metaballs.length; i++) {
            var mb = metaballs[i];
            // Если метабол вышел за границы, перемещаем его
            if (mb.x < mb.r || mb.x > width - mb.r) {
                mb.x = Math.random() * (width - 2 * mb.r) + mb.r;
            }
            if (mb.y < mb.r || mb.y > height - mb.r) {
                mb.y = Math.random() * (height - 2 * mb.r) + mb.r;
            }
            // Обновляем скорости в соответствии с новым размером экрана
            mb.vx = (Math.random() - 0.5) * newParams.speedMultiplier;
            mb.vy = (Math.random() - 0.5) * newParams.speedMultiplier;
        }
    }
    
    // Debounce для resize, чтобы не пересчитывать слишком часто
    var resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(handleResize, 150);
    });
    
    loop();
    
    function loop() {
        for (var i = 0; i < numMetaballs; i++) {
            var metaball = metaballs[i];
            metaball.x += metaball.vx;
            metaball.y += metaball.vy;
            
            if (metaball.x < metaball.r || metaball.x > width - metaball.r) metaball.vx *= -1;
            if (metaball.y < metaball.r || metaball.y > height - metaball.r) metaball.vy *= -1;
        }
        
        var dataToSendToGPU = new Float32Array(3 * numMetaballs);
        for (var i = 0; i < numMetaballs; i++) {
            var baseIndex = 3 * i;
            var mb = metaballs[i];
            dataToSendToGPU[baseIndex + 0] = mb.x;
            dataToSendToGPU[baseIndex + 1] = mb.y;
            dataToSendToGPU[baseIndex + 2] = mb.r;
        }
        gl.uniform3fv(metaballsHandle, dataToSendToGPU);
        
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        
        requestAnimationFrame(loop);
    }
    
    function compileShader(shaderSource, shaderType) {
        var shader = gl.createShader(shaderType);
        gl.shaderSource(shader, shaderSource);
        gl.compileShader(shader);
        
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            console.error("Shader compile failed:", gl.getShaderInfoLog(shader));
            return null;
        }
        
        return shader;
    }
    
    function getUniformLocation(program, name) {
        var uniformLocation = gl.getUniformLocation(program, name);
        if (uniformLocation === -1) {
            console.warn('Can not find uniform ' + name + '.');
        }
        return uniformLocation;
    }
    
    function getAttribLocation(program, name) {
        var attributeLocation = gl.getAttribLocation(program, name);
        if (attributeLocation === -1) {
            console.warn('Can not find attribute ' + name + '.');
        }
        return attributeLocation;
    }
    
    canvas.onmousemove = function(e) {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    };
})();

