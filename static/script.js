const COLLAPSED_LINES = 3;

function getCollapsedHeightPx(element) {
    const styles = window.getComputedStyle(element);
    const lineHeight = parseFloat(styles.lineHeight);
    const collapsed = Math.round(lineHeight * COLLAPSED_LINES);
    return collapsed;
}

function expandSection(element) {
    // Устанавливаем текущую высоту для запуска анимации
    element.style.maxHeight = element.scrollHeight + 'px';
}

function collapseSection(element) {
    element.style.maxHeight = getCollapsedHeightPx(element) + 'px';
}

function initHeights() {
    document.querySelectorAll('.post-content').forEach((content) => {
        const toggleBtn = content.nextElementSibling;
        const collapsedHeight = getCollapsedHeightPx(content);
        
        // Сначала применяем collapsed, чтобы блок был свернут
        const wasCollapsed = content.classList.contains('collapsed');
        if (wasCollapsed) {
            collapseSection(content);
        }
        
        // Временно убираем collapsed, чтобы проверить реальную высоту
        content.classList.remove('collapsed');
        content.style.maxHeight = 'none';
        
        // Ждем рефлоу для получения актуальной высоты
        requestAnimationFrame(() => {
            const fullHeight = content.scrollHeight;
            
            // Если контент помещается в свернутом виде, убираем кнопку и класс
            if (fullHeight <= collapsedHeight) {
                content.style.maxHeight = 'none';
                content.classList.remove('collapsed');
                if (toggleBtn && toggleBtn.classList.contains('toggle-btn')) {
                    toggleBtn.style.display = 'none';
                }
            } else {
                // Если контент не помещается, применяем collapsed и показываем кнопку
                content.classList.add('collapsed');
                collapseSection(content);
                if (toggleBtn && toggleBtn.classList.contains('toggle-btn')) {
                    toggleBtn.style.display = 'block';
                }
            }
        });
    });
}

function handleResize() {
    document.querySelectorAll('.post-content').forEach((content) => {
        const toggleBtn = content.nextElementSibling;
        const collapsedHeight = getCollapsedHeightPx(content);
        
        // Временно убираем ограничения для проверки
        const wasCollapsed = content.classList.contains('collapsed');
        const currentMaxHeight = content.style.maxHeight;
        content.style.maxHeight = 'none';
        content.classList.remove('collapsed');
        
        requestAnimationFrame(() => {
            const fullHeight = content.scrollHeight;
            
            // Если контент помещается в свернутом виде, убираем кнопку
            if (fullHeight <= collapsedHeight) {
                content.style.maxHeight = 'none';
                if (toggleBtn && toggleBtn.classList.contains('toggle-btn')) {
                    toggleBtn.style.display = 'none';
                }
            } else {
                // Восстанавливаем состояние
                if (wasCollapsed) {
                    content.classList.add('collapsed');
                    collapseSection(content);
                } else {
                    content.style.maxHeight = 'none';
                }
                if (toggleBtn && toggleBtn.classList.contains('toggle-btn')) {
                    toggleBtn.style.display = 'block';
                }
            }
        });
    });
}

window.addEventListener('DOMContentLoaded', () => {
    initHeights();

    document.querySelectorAll('.toggle-btn').forEach((button) => {
        button.addEventListener('click', () => {
            const postContent = button.previousElementSibling;
            const isCollapsed = postContent.classList.contains('collapsed');

            if (isCollapsed) {
                postContent.classList.remove('collapsed');
                // Сначала ставим вычисляемую высоту, затем по завершении анимации снимаем ограничение
                expandSection(postContent);
                const onEnd = (e) => {
                    if (e.propertyName === 'max-height') {
                        postContent.style.maxHeight = 'none';
                        postContent.removeEventListener('transitionend', onEnd);
                    }
                };
                postContent.addEventListener('transitionend', onEnd);
                button.textContent = 'Скрыть';
            } else {
                // Если было auto ('none'), зафиксируем текущую высоту, чтобы анимация пошла вверх
                if (postContent.style.maxHeight === '' || postContent.style.maxHeight === 'none') {
                    postContent.style.maxHeight = postContent.scrollHeight + 'px';
                    // Форсируем рефлоу для корректного старта анимации
                    // eslint-disable-next-line no-unused-expressions
                    postContent.offsetHeight;
                }
                postContent.classList.add('collapsed');
                collapseSection(postContent);
                button.textContent = 'Развернуть';
            }
        });
    });
});

window.addEventListener('resize', handleResize);
