$errorModal = $('#error-modal');
$errorModalMessage = $('#error-modal-message');
function showErrorMessage(text) {
    $errorModalMessage.html(text);
    $errorModal.modal('show');
}