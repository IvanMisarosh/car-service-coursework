// Wait for the document to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Select all table rows
    const rows = document.querySelectorAll('#customers-table tbody tr');

    // Loop through each row and add a click event listener
    rows.forEach(row => {
        row.addEventListener('click', function() {
            // Remove 'active' class from all rows
            rows.forEach(r => r.classList.remove('active'));

            // Add 'active' class to the clicked row
            row.classList.add('active');
        });
    });
});
