document.addEventListener('DOMContentLoaded', function() {
    var selectElement = document.getElementById('combobox');
    selectElement.addEventListener('change', function() {
        var selectedOption = this.options[this.selectedIndex];
        var url = selectedOption.getAttribute('data-url');
        if (url) {
            window.location.href = url;
        }
    });
});

