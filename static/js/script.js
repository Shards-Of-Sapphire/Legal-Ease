const form = document.getElementById("uploadForm");
const resultsDiv = document.getElementById("results");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);

    resultsDiv.innerHTML = `
    <div class="card mt-4">
        <div class="card-body">
            <h3>Summary</h3>
            <div class="alert alert-success">
                ${data.summary}
            </div>
        </div>
    </div>
`;

    try {
        const response = await fetch("https://legal-ease-eight-teal.vercel.app/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!data.success) {
            resultsDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            return;
        }

        renderResults(data);

    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">Server error</div>`;
    }
});

function renderResults(data) {
    let clausesHTML = "";

    if (data.key_clauses && data.key_clauses.length > 0) {
        clausesHTML = `
            <h4 class="mt-4">Key Clauses</h4>
            <div class="row">
                ${data.key_clauses.map(clause => `
                    <div class="card">
                        <div class="card-body">
                            <h6>${clause.type}</h6>
                            <p>${clause.content}</p>
                        </div>
                    </div>
                `).join("")}
            </div>
        `;
    }

    resultsDiv.innerHTML = `
        <div class="card mt-4">
            <div class="card-body">
                <h3>Summary</h3>
                <div class="alert alert-success">
                    ${data.summary}
                </div>
                ${clausesHTML}
            </div>
        </div>
    `;
}
window.scrollTo({
    top: resultsDiv.offsetTop,
    behavior: "smooth"
});
