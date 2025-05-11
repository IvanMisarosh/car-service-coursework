document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelectorAll('#customers-table tbody tr');

    rows.forEach(row => {
        row.addEventListener('click', function() {
            rows.forEach(r => r.classList.remove('active'));
            row.classList.add('active');
        });
    });
});

// Add event listener for custom events from CarAddView
document.addEventListener('htmx:afterSwap', function(event) {
    // Check if the event has a showMessage trigger
    const triggersString = event.detail.xhr.getResponseHeader('HX-Trigger');
    if (triggersString) {
        const triggers = JSON.parse(triggersString);
        
        // Handle showing success message
        if (triggers.showMessage) {
            const formContainer = document.getElementById('add-car-form-container');
            formContainer.innerHTML = triggers.showMessage;
        }
        
        // Handle updating customer details
        if (triggers.updateCustomerDetails) {
            const customerDetailsContainer = document.getElementById('selected-customer-details');
            customerDetailsContainer.innerHTML = triggers.updateCustomerDetails;
        }
    }
});