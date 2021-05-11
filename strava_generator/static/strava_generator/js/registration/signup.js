$(document).ready(() => {
    initInputFocusControl();
    initInputFieldsBehaviour();
    initOnFormSubmit();
    initPopover();
});


$signupForm = $('#sign-up-form');
function initInputFocusControl() {
    $signupForm.on('keypress', '.form-group', function (e) {
        if (e.which === 13) {
            const $nextInput = $(this).next().find('input');
            if ($nextInput.length !== 0) {
                e.preventDefault();
                $nextInput.focus();
            }
        }
    });
}


function initInputFieldsBehaviour() {
    $signupForm.find('input').on('focus', function (e) {
        $(this).removeClass('border-danger');
    });
}


function initOnFormSubmit() {
    $signupForm.submit((e) => {
        $signupForm.find('.error-message').remove();
        $signupForm.find('input').removeClass('border-danger');

        validateUsername();
        validatePassword();
        validatePasswordConfirm();
        validateUsageToken();

        if ($signupForm.find('.error-message').length !== 0) {
            $signupForm.find('input').blur();
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

$passwordConfirm = $('#password-confirm');
function validatePasswordConfirm() {
    const password = $password.val();
    const passwordConfirm = $passwordConfirm.val();

    if (passwordConfirm !== password) {
        addErrorMessage($passwordConfirm.parent(), 'Password doesn\'t match');
        $passwordConfirm.addClass('border-danger');
    } else if (passwordConfirm.length === 0) {
        addErrorMessage($passwordConfirm.parent(), 'Confirm password is empty');
        $passwordConfirm.addClass('border-danger');
    } else if (passwordConfirm.length < 6) {
        addErrorMessage($passwordConfirm.parent(), 'Confirm password length must be at least 6 characters');
        $passwordConfirm.addClass('border-danger');
    }
}

$usageToken = $('#usage-token');
function validateUsageToken() {
    const usageToken = $usageToken.val();

    console.log(usageToken.length);
    if (usageToken.length === 0) {
        addErrorMessage($usageToken.parent(), 'Usage token is empty');
        $usageToken.addClass('border-danger');
    }
}


$contactInfo = $('.contact-info');
function initPopover() {
    $contactInfo.popover({
        container: 'body',
        html: true,
        content: `Contact <a href='https://t.me/iamdubrovskii'>@iamdubrovskii</a> on how to get usage tokens`,
        trigger: 'focus',
        placement: 'top',
    });
}