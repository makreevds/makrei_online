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
    
    var numMetaballs = 25;
    var metaballs = [];
    
    for (var i = 0; i < numMetaballs; i++) {
        var radius = Math.random() * 80 + 30;
        metaballs.push({
            x: Math.random() * (width - 2 * radius) + radius,
            y: Math.random() * (height - 2 * radius) + radius,
            vx: (Math.random() - 0.5) * 2,
            vy: (Math.random() - 0.5) * 2,
            r: radius * 0.75
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
    }
    
    window.addEventListener('resize', handleResize);
    
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

