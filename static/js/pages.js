
document.addEventListener("DOMContentLoaded", function() {
    var currentPage = 1;
    var rowsPerPage = 10; 
    var tableBody = document.querySelector("table.table tbody");
    var rows = Array.from(tableBody.getElementsByTagName("tr"));
    var totalPages = Math.ceil(rows.length / rowsPerPage);
    function showCurrentPage() {
        var startIndex = (currentPage - 1) * rowsPerPage;
        var endIndex = startIndex + rowsPerPage;
        rows.forEach(function(row, index) {
            if (index >= startIndex && index < endIndex) {
                row.style.display = "table-row";
            } else {
                row.style.display = "none";
            }
        });
        // Actualiza el número de la página actual en el span
        var currentPageSpan = document.getElementById("current-page");
        currentPageSpan.textContent = "Page " + currentPage + " of " + totalPages;
    }
    function updatePageButtons() {
        var prevButton = document.getElementById("prev-page-btn");
        var nextButton = document.getElementById("next-page-btn");
        prevButton.disabled = (currentPage === 1);
        nextButton.disabled = (currentPage === totalPages);
    }
    function goToPreviousPage() {
        if (currentPage > 1) {
            currentPage--;
            showCurrentPage();
            updatePageButtons();
        }
    }
    function goToNextPage() {
        if (currentPage < totalPages) {
            currentPage++;
            showCurrentPage();
            updatePageButtons();
        }
    }
    var prevButton = document.getElementById("prev-page-btn");
    var nextButton = document.getElementById("next-page-btn");
    prevButton.addEventListener("click", goToPreviousPage);
    nextButton.addEventListener("click", goToNextPage);
    // Llama a showCurrentPage al cargar la página
    showCurrentPage();
    updatePageButtons();
});
