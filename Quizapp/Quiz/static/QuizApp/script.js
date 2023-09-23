
     function togglePresetsForm() {
        var presetsForm = document.getElementById('presets-form');
        var scoreTable = document.getElementById('score-table');

        if (scoreTable.style.display === 'block') {
            scoreTable.style.display = 'none';
        }

        if (presetsForm.style.display === 'none') {
            presetsForm.style.display = 'block';
        } else {
            presetsForm.style.display = 'none';
        }
    }
    function showGrades() {
    var gradesTable = document.getElementById("grades-table");
    if (gradesTable.style.display === "none") {
        gradesTable.style.display = "block";
    } else {
        gradesTable.style.display = "none";
    }
}
     function toggleAddDisciplineForm() {
    var form = document.getElementById("add-discipline-form");
    if (form.style.display === "none") {
      form.style.display = "block";
    } else {
      form.style.display = "none";
    }
  }
    document.getElementById("test-list-link").addEventListener("click", function (event) {
      event.preventDefault();
      var table = document.getElementById("test-list-table");

      if (table.style.display === "none") {
        table.style.display = "block";
      } else {
        table.style.display = "none";
      }
    });

    function toggleExamForm() {
      var examForm = document.getElementById("exam-form");

      if (examForm.style.display === "none") {
        examForm.style.display = "block";
      } else {
        examForm.style.display = "none";
      }
    }


    var disciplineCards = document.getElementById("discipline-cards");
    var topicCards = document.getElementById("topic-cards");
    var examCards = document.getElementById("exam-cards");
    var topicSubmenu = document.getElementById("topic-submenu");

    function toggleDisciplineOptions() {
      if (disciplineCards.style.display === "none") {
        disciplineCards.style.display = "block";
        topicCards.style.display = "none";
        examCards.style.display = "none";
      } else {
        disciplineCards.style.display = "none";
      }
    }

    function toggleExamCards() {
      if (examCards.style.display === "none") {
        examCards.style.display = "block";
        disciplineCards.style.display = "none";
        topicCards.style.display = "none";
      } else {
        examCards.style.display = "none";
      }
    }

    function toggleTopicCards() {
      if (topicCards.style.display === "none") {
        topicCards.style.display = "block";
        disciplineCards.style.display = "none";
        topicSubmenu.style.display = "block";
        examCards.style.display = "none";
      } else {
        topicCards.style.display = "none";
      }
    }

    function toggleTopicForm() {
      var topicForm = document.getElementById("topic-form");
      var topicButtons = document.getElementById("topic-buttons");

      if (topicForm.style.display === "none") {
        topicForm.style.display = "block";
        topicButtons.style.display = "block";
      } else {
        topicForm.style.display = "none";
        topicButtons.style.display = "none";
      }
    }

    function toggleTopicList() {
      var topicList = document.getElementById("topic-list");
      var topicButtons = document.getElementById("topic-buttons");

      if (topicList.style.display === "none") {
        topicList.style.display = "block";
        topicButtons.style.display = "block";
      } else {
        topicList.style.display = "none";
        topicButtons.style.display = "none";
      }
    }

   function showScoreTable() {
        var presetsForm = document.getElementById('presets-form');
        var scoreTable = document.getElementById('score-table');

        if (presetsForm.style.display === 'block') {
            presetsForm.style.display = 'none';
        }

        if (scoreTable.style.display === 'none') {
            scoreTable.style.display = 'block';
        } else {
            scoreTable.style.display = 'none';
        }
    }

    function showSidebarButtons() {
      var sidebarButtons = document.querySelectorAll('.sidebar a');
      sidebarButtons.forEach(function (button, index) {
        setTimeout(function () {
          button.classList.add('show');
        }, index * 100);
      });
    }

    window.onload = function () {
      showSidebarButtons();
    };
    function toggleDisciplineList() {
  var disciplineList = document.getElementById('discipline-list');

  if (disciplineList.style.display === 'none' || disciplineList.style.display === '') {
    disciplineList.style.display = 'block';
  } else {
    disciplineList.style.display = 'none';
  }
}
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
          return parseFloat(valueB) - parseFloat(valueA);
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
