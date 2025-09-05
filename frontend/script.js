document.addEventListener('DOMContentLoaded', function () {
    // Handle login form submission
    document.getElementById('loginForm').addEventListener('submit', function (e) {
        e.preventDefault();
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();

        // Dummy validation
        if (username === 'admin' && password === 'admin') {
            alert('Login successful!');
        } else {
            alert('Invalid credentials. Try admin/admin.');
        }
    });

    // Handle idea form submission
    document.getElementById('ideaForm').addEventListener('submit', function (e) {
        e.preventDefault();

        const idea = {
            title: document.getElementById('ideaTitle').value.trim(),
            description: document.getElementById('ideaDescription').value.trim(),
            category: document.getElementById('ideaCategory').value.trim(),
            impact: document.getElementById('ideaImpact').value
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

    // Load ideas from server
    function loadIdeas() {
        fetch('/ideas')
            .then(response => response.json())
            .then(data => {
                const ideaList = document.getElementById('ideaList');
                ideaList.innerHTML = '';

                data.forEach((idea, index) => {
                    const card = document.createElement('div');
                    card.className = 'col-md-6';

                    card.innerHTML = `
                        <div class="card h-100" style="cursor:pointer;">
                            <div class="card-body">
                                <h5 class="card-title">${idea.title}</h5>
                                <p class="card-text clamp-text">${idea.description}</p>
                                <p><strong>Category:</strong> ${idea.category}</p>
                                <p><strong>Impact:</strong> ${idea.impact}</p>
                            </div>
                        </div>
                    `;
                    // Add click listener to open modal with full info
                    card.addEventListener('click', () => {
                        const modalTitle = document.getElementById('ideaModalLabel');
                        const modalBody = document.getElementById('ideaModalBody');
                        const modalMeta = document.getElementById('ideaModalMeta');

                        modalTitle.textContent = idea.title;
                        modalBody.textContent = idea.description;
                        modalMeta.textContent = `Category: ${idea.category} | Impact: ${idea.impact}`;

                        const modal = new bootstrap.Modal(document.getElementById('ideaModal'));
                        modal.show();
                    });

                    ideaList.appendChild(card);
                });
            });
    }

    // Initial load
    loadIdeas();
});
