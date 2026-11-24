/* ==========================================================
   StudyRoomBooking — клиентская валидация и UX (Темы 6, 10)
   Ошибки выводятся рядом с полем (не через alert()).
   ========================================================== */
document.addEventListener('DOMContentLoaded', function () {
    // 1. Валидация формы регистрации (email, пароль, подтверждение)
    var registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function (e) {
            var emailField = registerForm.querySelector('input[name="email"]');
            var p1 = registerForm.querySelector('input[name="password1"]');
            var p2 = registerForm.querySelector('input[name="password2"]');
            clearErrors(registerForm);
            var ok = true;
            if (emailField && !/^\S+@\S+\.\S+$/.test(emailField.value)) {
                showError(emailField, 'Введите корректный email (пример: user@mail.ru)');
                ok = false;
            }
            if (p1 && p2 && p1.value !== p2.value) {
                showError(p2, 'Пароли не совпадают');
                ok = false;
            }
            if (p1 && (p1.value.length < 8)) {
                showError(p1, 'Пароль должен содержать минимум 8 символов');
                ok = false;
            }
            if (!ok) e.preventDefault();
        });
    }

    // 2. Валидация формы сброса пароля
    var resetForm = document.getElementById('reset-form');
    if (resetForm) {
        resetForm.addEventListener('submit', function (e) {
            var pass = resetForm.querySelector('input[name="password"]');
            var conf = resetForm.querySelector('input[name="confirm_password"]');
            clearErrors(resetForm);
            var ok = true;
            if (pass && conf && pass.value !== conf.value) {
                showError(conf, 'Пароли не совпадают');
                ok = false;
            }
            if (pass && pass.value.length < 8) {
                showError(pass, 'Пароль должен содержать минимум 8 символов');
                ok = false;
            }
            if (!ok) e.preventDefault();
        });
    }

    // 3. Подтверждение удаления (форма с классом confirm-delete)
    document.querySelectorAll('form.confirm-delete').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!window.confirm('Вы уверены, что хотите удалить эту запись? Действие необратимо.')) {
                e.preventDefault();
            }
        });
    });

    // Вспомогательные функции: ошибка рядом с полем, а не всплывающее окно
    function showError(input, message) {
        input.classList.add('invalid');
        var err = document.createElement('p');
        err.className = 'error-text';
        err.textContent = message;
        input.parentElement.appendChild(err);
    }

    function clearErrors(form) {
        form.querySelectorAll('.error-text').forEach(function (el) { el.remove(); });
        form.querySelectorAll('.invalid').forEach(function (el) { el.classList.remove('invalid'); });
    }

    // 4. Валидация формы бронирования (Тема 8)
    var bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function (e) {
            var date = bookingForm.querySelector('input[name="date"]');
            var start = bookingForm.querySelector('input[name="time_start"]');
            var end = bookingForm.querySelector('input[name="time_end"]');
            clearErrors(bookingForm);
            var ok = true;
            if (start && end && start.value && end.value && start.value >= end.value) {
                showError(end, 'Время окончания должно быть позже времени начала');
                ok = false;
            }
            if (date && date.value && new Date(date.value) < new Date(new Date().toDateString())) {
                showError(date, 'Нельзя бронировать на прошедшую дату');
                ok = false;
            }
            if (!ok) e.preventDefault();
        });
    }

    // 5. Мобильное меню
    var navToggle = document.getElementById('nav-toggle');
    var navMenu = document.getElementById('nav-menu');
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            var open = navMenu.classList.toggle('nav-open');
            navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
    }
});
