document.addEventListener('DOMContentLoaded', function () {
  const currentUsername = localStorage.getItem("username") || "";
  const SUPERADMIN_USERNAME = "Shama08";  // Change as needed

  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const username = document.getElementById('username').value.trim();
      const password = document.getElementById('password').value.trim();

      if (username === 'admin' && password === 'admin') {
        localStorage.setItem("username", username);
        alert('Login successful!');
        location.reload();
      } else {
        alert("Invalid credentials.");
      }
    });
  }

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
            ideaForm.reset();
            loadIdeas();
          } else {
            alert('Failed to submit idea.');
          }
        })
        .catch(err => {
          console.error("Error submitting idea:", err);
          alert('Error submitting idea.');
        });
    });
  }

  function loadIdeas() {
    const ideaList = document.getElementById('ideaList');
    if (!ideaList) return;

    fetch('/ideas')
      .then(response => response.json())
      .then(data => {
        ideaList.innerHTML = '';

        if (!Array.isArray(data) || data.length === 0) {
          ideaList.innerHTML = `
            <div class="col-12">
              <div class="alert alert-info text-center">No ideas submitted yet.</div>
            </div>
          `;
          return;
        }

        data.forEach((idea) => {
          const card = document.createElement('div');
          card.className = 'col-md-6 col-lg-4 d-flex align-items-stretch';

          card.innerHTML = `
            <div class="card shadow-sm h-100 position-relative" role="button" tabindex="0">
              <div class="card-body d-flex flex-column">
                <h5 class="card-title">${idea.title}</h5>
                <p class="card-text clamp-2 flex-grow-1">${idea.description}</p>
                <p><strong>Category:</strong> ${idea.category}</p>
                <p><strong>Impact:</strong> ${idea.impact}</p>
                <p class="text-muted small mt-auto">Author: ${idea.author || "Unknown"}</p>
                <button class="btn btn-sm btn-outline-danger delete-btn" data-id="${idea.id}">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>
          `;

          // Open modal on card click
          card.querySelector(".card").addEventListener('click', (event) => {
            if (event.target.closest(".delete-btn")) return;

            const modalTitle = document.getElementById('ideaModalLabel');
            const modalBody = document.getElementById('ideaModalBody');
            const modalMeta = document.getElementById('ideaModalMeta');

            if (!modalTitle || !modalBody || !modalMeta) return;

            modalTitle.textContent = idea.title;
            modalBody.textContent = idea.description;
            modalMeta.textContent = `Category: ${idea.category} | Impact: ${idea.impact}`;

            const modal = new bootstrap.Modal(document.getElementById('ideaModal'));
            modal.show();
          });

          // Handle delete
          card.querySelector(".delete-btn").addEventListener("click", async (e) => {
            e.stopPropagation();

            const ideaId = e.target.getAttribute("data-id");

            if (currentUsername !== SUPERADMIN_USERNAME) {
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
                loadIdeas();
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
      })
      .catch(error => {
        console.error("Error loading ideas:", error);
        alert("Failed to load ideas.");
      });
  }

  // Initial ideas load
  if (document.getElementById('ideaList')) {
    loadIdeas();
  }
});
