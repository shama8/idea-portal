document.addEventListener('DOMContentLoaded', function () {
  const currentUsername = localStorage.getItem("username") || "";  // Assume login stored username

  // Handle login form submission
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const username = document.getElementById('username').value.trim();
      const password = document.getElementById('password').value.trim();

      // Dummy validation
      if (username === 'admin' && password === 'admin') {
        localStorage.setItem("username", username);  // Store for later
        alert('Login successful!');
      } else {
        alert('Invalid credentials. Try admin/admin.');
      }
    });
  }

  // Handle idea form submission
  const ideaForm = document.getElementById('ideaForm');
  if (ideaForm) {
    ideaForm.addEventListener('submit', function (e) {
      e.preventDefault();

      const idea = {
        title: document.getElementById('ideaTitle').value.trim(),
        description: document.getElementById('ideaDescription').value.trim(),
        category: document.getElementById('ideaCategory').value.trim(),
        impact: document.getElementById('ideaImpact').value,
        author: currentUsername || "Anonymous"
      };

      fetch('/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(idea)
      })
        .then(response => {
          if (response.ok) {
            alert('Idea submitted successfully!');
            document.getElementById('ideaForm').reset();
            loadIdeas();
          } else {
            alert('Failed to submit idea.');
          }
        });
    });
  }

  // Load ideas from server
  function loadIdeas() {
    fetch('/ideas')
      .then(response => response.json())
      .then(data => {
        const ideaList = document.getElementById('ideaList');
        ideaList.innerHTML = '';

        data.forEach((idea) => {
          const card = document.createElement('div');
          card.className = 'col-md-6';

          card.innerHTML = `
            <div class="card h-100" style="cursor:pointer; position: relative;">
              <div class="card-body">
                <h5 class="card-title">${idea.title}</h5>
                <p class="card-text clamp-text">${idea.description}</p>
                <p><strong>Category:</strong> ${idea.category}</p>
                <p><strong>Impact:</strong> ${idea.impact}</p>
                <button class="btn btn-sm btn-outline-danger delete-btn" style="position: absolute; top: 10px; right: 10px;" data-id="${idea.id}">
                  🗑️
                </button>
              </div>
            </div>
          `;

          // Modal view
          card.querySelector(".card").addEventListener('click', (event) => {
            // prevent modal if delete button was clicked
            if (event.target.classList.contains("delete-btn")) return;

            const modalTitle = document.getElementById('ideaModalLabel');
            const modalBody = document.getElementById('ideaModalBody');
            const modalMeta = document.getElementById('ideaModalMeta');

            modalTitle.textContent = idea.title;
            modalBody.textContent = idea.description;
            modalMeta.textContent = `Category: ${idea.category} | Impact: ${idea.impact}`;

            const modal = new bootstrap.Modal(document.getElementById('ideaModal'));
            modal.show();
          });

          // Delete handler
          card.querySelector(".delete-btn").addEventListener("click", async (e) => {
            e.stopPropagation();  // Prevent modal trigger

            const ideaId = e.target.getAttribute("data-id");

            if (currentUsername !== "Shama08") {
              alert("You are not authorized to delete this idea.");
              return;
            }

            const confirmDelete = confirm("Are you sure you want to delete this idea?");
            if (!confirmDelete) return;

            try {
              const response = await fetch(`/api/delete-idea/${ideaId}`, {
                method: "DELETE",
                headers: {
                  "Content-Type": "application/json"
                },
                body: JSON.stringify({ username: currentUsername })
              });

              const result = await response.json();

              if (response.ok) {
                alert("Idea deleted successfully.");
                loadIdeas();  // Refresh list
              } else {
                alert(result.error || "Failed to delete the idea.");
              }
            } catch (err) {
              console.error(err);
              alert("Error occurred while deleting the idea.");
            }
          });

          ideaList.appendChild(card);
        });
      });
  }

  // Initial load
  if (document.getElementById('ideaList')) {
    loadIdeas();
  }
});
