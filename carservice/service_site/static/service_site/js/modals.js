document.addEventListener('DOMContentLoaded', function () {

    document.getElementById('serviceSearchModal').addEventListener('hidden.bs.modal', function () {
        document.getElementById('staged-visit-services').innerHTML = '';
    });

});
