
// Function to initialize toasts
function initializeToasts() {
    var toastElements = document.querySelectorAll('.toast');
    toastElements.forEach(function(toastElement) {
        var toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 3000
        });
        toast.show();
    });
    toastElements.forEach(function(toastElement) {
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove(); // Remove the toast element from the DOM after hiding
        });
    });
}