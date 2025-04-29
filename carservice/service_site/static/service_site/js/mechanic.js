document.addEventListener('DOMContentLoaded', function () {

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
    
    // Run on initial page load
    document.addEventListener('DOMContentLoaded', initializeToasts);
    
    // // Run when htmx swaps content
    document.body.addEventListener('htmx:afterSwap', initializeToasts);

});
