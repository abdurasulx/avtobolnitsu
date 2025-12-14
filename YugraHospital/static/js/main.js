// Валидация формы
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[id$="Form"]');
    forms.forEach(form => {
        form.addEventListener('submit', validateForm);
    });
});

function validateForm(event) {
    const form = event.target;
    let isValid = true;

    // Проверка, что имя не пустое
    const nameFields = form.querySelectorAll('input[name="first_name"], input[name="last_name"], input[name="name"]');
    nameFields.forEach(field => {
        if (!field.value.trim()) {
            alert('Имя не может быть пустым!');
            isValid = false;
        }
    });

    // Формат телефона: +7 XXX XXX XX XX
const phoneField = form.querySelector('input[name="phone"]');
if (phoneField && !/^\+7\s?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$/.test(phoneField.value)) {
    alert('Формат номера телефона: +7 (495) 539-55-19');
    isValid = false;
}

if (!isValid) {
    event.preventDefault(); // formani yuborishni to‘xtatish
}   

    // Дата: дата рождения должна быть раньше сегодняшней
    const birthDateField = form.querySelector('input[name="birth_date"]');
    if (birthDateField) {
        const birthDate = new Date(birthDateField.value);
        if (birthDate >= new Date()) {
            alert('Дата рождения должна быть раньше сегодняшней даты!');
            isValid = false;
        }
    }

    if (!isValid) {
        event.preventDefault();
    }
}

// Для мобильной навигации (просто)
function toggleNav() {
    // Если нужно, добавьте responsive nav
}