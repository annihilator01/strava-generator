$(document).ready(() => {
    initInputFocusControl();
    initInputFieldsBehaviour();
    initOnFormSubmit();
    initPopover();
});


$usageTokenForm = $('#usage-token-form');
function initInputFocusControl() {
    $usageTokenForm.on('keypress', '.form-group', function (e) {
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
    $usageTokenForm.find('input').on('focus', function (e) {
        $(this).removeClass('border-danger');
    });
}


function initOnFormSubmit() {
    $usageTokenForm.submit((e) => {
        $usageTokenForm.find('.error-message').remove();
        $usageTokenForm.find('input').removeClass('border-danger');

        validateUsageToken();

        if ($usageTokenForm.find('.error-message').length !== 0) {
            $usageTokenForm.find('input').blur();
            e.preventDefault();
        }
    })
}


function addErrorMessage($el, errorMessage) {
    $el.children('.error-message').remove();
    $el.after(`<span class="error-message">${errorMessage}</span>`);
}


$usageToken = $('#usage-token');
function validateUsageToken() {
    const usageToken = $usageToken.val();

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
        content: `Contact <a href='https://t.me/iamdubrovskii'>@iamdubrovskii</a> on how to get new usage tokens`,
        trigger: 'focus',
        placement: 'top',
    });
}