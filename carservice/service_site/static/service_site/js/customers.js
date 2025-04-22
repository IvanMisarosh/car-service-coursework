document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelectorAll('#customers-table tbody tr');

    rows.forEach(row => {
        row.addEventListener('click', function() {
            rows.forEach(r => r.classList.remove('active'));
            row.classList.add('active');
        });
    });
});
