// Profile page JavaScript

function closeUpdateModal() {
    var modal = document.getElementById('update-weight-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Закрытие модального окна при клике вне его
window.onclick = function(event) {
    var modal = document.getElementById('update-weight-modal');
    if (event.target == modal) {
        closeUpdateModal();
    }
}

