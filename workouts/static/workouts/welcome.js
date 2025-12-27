// Welcome page JavaScript

function showForm(formType) {
    // Скрываем все формы
    document.querySelectorAll('.auth-form').forEach(form => {
        form.classList.remove('active');
    });
    // Убираем активный класс у всех табов
    document.querySelectorAll('.auth-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Показываем нужную форму и активируем таб
    if (formType === 'login') {
        document.getElementById('login-form').classList.add('active');
        document.querySelectorAll('.auth-tab')[0].classList.add('active');
    } else {
        document.getElementById('register-form').classList.add('active');
        document.querySelectorAll('.auth-tab')[1].classList.add('active');
    }
}

// Если есть ошибки регистрации, показываем форму регистрации
document.addEventListener('DOMContentLoaded', function() {
    var showRegister = document.body.getAttribute('data-show-register') === 'true';
    if (showRegister) {
        showForm('register');
    }
});

