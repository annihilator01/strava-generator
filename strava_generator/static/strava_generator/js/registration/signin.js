$(document).ready(() => {
    initInputFocusControl();
    initInputFieldsBehaviour();
    initOnFormSubmit();
});


$signinForm = $('#sign-in-form');
function initInputFocusControl() {
    $signinForm.on('keypress', '.form-group', function (e) {
        if (e.which === 13) {
            const $nextInput = $(this).next().find('input');
            if ($nextInput.length !== 0) {
                $nextInput.focus();
                e.preventDefault();
            }
        }
    });
}


function initInputFieldsBehaviour() {
    $signinForm.find('input').on('focus', function (e) {
        $(this).removeClass('border-danger');
    });
}


function initOnFormSubmit() {
    $signinForm.submit((e) => {
        $signinForm.find('.error-message').remove();
        $signinForm.find('input').removeClass('border-danger');

        validateUsername();
        validatePassword();

        if ($signinForm.find('.error-message').length !== 0) {
            $signinForm.find('input').blur();
            e.preventDefault();
        }
    })
}


function addErrorMessage($el, errorMessage) {
    $el.children('.error-message').remove();
    $el.after(`<span class="error-message">${errorMessage}</span>`);
}

$username = $('#username');
function validateUsername() {
    const username = $username.val();
    if (username.length === 0) {
        addErrorMessage($username.parent(), 'Username is empty');
        $username.addClass('border-danger');
    } else if (username.length < 6) {
        addErrorMessage($username.parent(), 'Username length must be at least 6 characters');
        $username.addClass('border-danger');
    }
}

$password = $('#password');
function validatePassword() {
    const password = $password.val();
    if (password.length === 0) {
        addErrorMessage($password.parent(), 'Password is empty');
        $password.addClass('border-danger');
    } else if (password.length < 6) {
        addErrorMessage($password.parent(), 'Password length must be at least 6 characters');
        $password.addClass('border-danger');
    }
}