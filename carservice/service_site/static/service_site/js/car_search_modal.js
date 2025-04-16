document.addEventListener('DOMContentLoaded', function () {

    document.getElementById('serviceSearchModal').addEventListener('hidden.bs.modal', function () {
        document.getElementById('staged-visit-services').innerHTML = '';
    });

    document.getElementById('carSearchModal').addEventListener('hidden.bs.modal', function () {
        document.getElementById('selected-car-details').innerHTML = '';
    });
});
