const filterNameButton = document.getElementById("filter-name-button");
    const filterLastNameButton = document.getElementById("filter-lastname-button");
    const filterScoresButton = document.getElementById("filter-scores-button");
    const filterGradesButton = document.getElementById("filter-grades-button");
    const tableBody = document.querySelector(".container tbody");

    filterNameButton.addEventListener("click", function () {
      sortTableByColumn(tableBody, 0);
    });

    filterLastNameButton.addEventListener("click", function () {
      sortTableByColumn(tableBody, 1);
    });

    filterScoresButton.addEventListener("click", function () {
      sortTableByColumn(tableBody, 4);
    });

    filterGradesButton.addEventListener("click", function () {
      sortTableByColumn(tableBody, 5);
    });

    function sortTableByColumn(tableBody, columnIndex) {
      const rows = Array.from(tableBody.querySelectorAll("tr"));

      rows.sort((a, b) => {
        const valueA = a.cells[columnIndex].textContent.toLowerCase();
        const valueB = b.cells[columnIndex].textContent.toLowerCase();

        if (columnIndex === 4 || columnIndex === 5) {
          return parseFloat(valueB) - parseFloat(valueA)
        } else {
          return valueA.localeCompare(valueB);
        }
      });

      rows.forEach(row => {
        tableBody.appendChild(row);
      });
    }

    const searchInput = document.getElementById("search-name");
    const tableRows = document.querySelectorAll(".container tbody tr");

    searchInput.addEventListener("input", function () {
      const searchTerm = searchInput.value.trim().toLowerCase();

      tableRows.forEach(row => {
        const fullName = row.getAttribute("data-fullname");

        if (fullName.includes(searchTerm)) {
          row.style.display = "table-row";
        } else {
          row.style.display = "none";
        }
      });
    });