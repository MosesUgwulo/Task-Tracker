const BASE_URL = "http://127.0.0.1:8000";

// Escapes special characters so task data can safely be stored in HTML data-* attributes.
// Without this, characters like " or & would break the HTML attribute and corrupt the value.
function escapeAttr(str) {
    return (str || "").replace(/&/g, "&amp;").replace(/"/g, "&quot;");
}

// Wait for the DOM to be ready before attaching event listeners or fetching tasks
document.addEventListener("DOMContentLoaded", () => {
    getTasks();

    document.getElementById("task-form").addEventListener("submit", async (e) => {
        e.preventDefault(); // Prevent the default form submission which would reload the page

        const name = document.getElementById("task-name").value.trim();
        const description = document.getElementById("task-description").value.trim() || null; // Send null if empty so the backend treats it as optional
        const due_date = document.getElementById("task-due-date").value || null;               // Same here
        const status = document.getElementById("task-status").value;

        try {
            const response = await fetch(BASE_URL + "/tasks", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, description, status, due_date }),
            });
            if (!response.ok) throw new Error(await response.text()); // fetch() doesn't throw on 4xx/5xx, so we check response.ok manually
            e.target.reset();
            getTasks(); // Refresh the list to show the newly added task
        } catch (err) {
            console.error("Failed to create task:", err);
            alert("Failed to add task. Please try again.");
        }
    });
});

async function getTasks() {
    try {
        const response = await fetch(BASE_URL + "/tasks");
        if (!response.ok) throw new Error(await response.text());
        const tasks = await response.json();
        const taskList = document.getElementById("task-list");

        // Task data is stored in data-* attributes on the card element instead of inline onclick
        // strings. This fixes a bug where special characters like apostrophes (e.g. "Mike's laptop")
        // would break the string passed to onclick="showEditForm('Mike's laptop'...)".
        taskList.innerHTML = tasks.map(task => `
            <div class="task-card"
                data-id="${task.id}"
                data-name="${escapeAttr(task.name)}"
                data-description="${escapeAttr(task.description)}"
                data-due-date="${escapeAttr(task.due_date)}"
                data-status="${task.status}">
                <div>
                    <h3>${task.name}</h3>
                    ${task.description ? `<p>${task.description}</p>` : ""}
                    ${task.due_date ? `<p>Due: ${task.due_date}</p>` : ""}
                    <span class="status status-${task.status}">${task.status.replace("_", " ")}</span>
                </div>
                <div class="card-actions">
                    <button class="edit-btn">Edit</button>
                    <button class="delete-btn">&#x2715;</button>
                </div>
            </div>
        `).join("");

        // Attach event listeners after rendering since the buttons are newly created each time
        taskList.querySelectorAll(".edit-btn").forEach(btn => {
            btn.addEventListener("click", () => showEditForm(btn.closest(".task-card")));
        });

        taskList.querySelectorAll(".delete-btn").forEach(btn => {
            btn.addEventListener("click", () => deleteTask(btn.closest(".task-card").dataset.id));
        });
    } catch (err) {
        console.error("Failed to load tasks:", err);
        alert("Failed to load tasks. Is the server running?");
    }
}

// Replaces the task card content with an inline edit form pre-filled with the current values.
// Values are read from data-* attributes on the card, not from inline onclick parameters,
// so special characters in the task data are handled safely.
function showEditForm(card) {
    // data-due-date becomes dueDate in JS (browsers auto-convert kebab-case to camelCase)
    const { id, name, description, dueDate, status } = card.dataset;

    card.innerHTML = `
        <div class="edit-form">
            <input type="text" class="edit-name" value="${escapeAttr(name)}" placeholder="Name" required>
            <input type="text" class="edit-desc" value="${escapeAttr(description)}" placeholder="Description (optional)">
            <input type="date" class="edit-due" value="${dueDate}">
            <select class="edit-status">
                <option value="todo" ${status === "todo" ? "selected" : ""}>Todo</option>
                <option value="in_progress" ${status === "in_progress" ? "selected" : ""}>In Progress</option>
                <option value="done" ${status === "done" ? "selected" : ""}>Done</option>
            </select>
        </div>
        <div class="card-actions">
            <button class="save-btn">Save</button>
            <button class="cancel-btn">Cancel</button>
        </div>
    `;

    // Attach listeners after re-rendering the card's innerHTML
    card.querySelector(".save-btn").addEventListener("click", () => saveTask(id, card));
    card.querySelector(".cancel-btn").addEventListener("click", () => getTasks()); // Cancel just re-fetches and re-renders the original list
}

async function saveTask(id, card) {
    // Read values directly from the DOM inputs rather than any inline attributes
    const name = card.querySelector(".edit-name").value.trim();
    const description = card.querySelector(".edit-desc").value.trim() || null;
    const due_date = card.querySelector(".edit-due").value || null;
    const status = card.querySelector(".edit-status").value;

    try {
        const response = await fetch(BASE_URL + "/tasks/" + id, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, description, status, due_date }),
        });
        if (!response.ok) throw new Error(await response.text());
        getTasks(); // Refresh the list to show the updated task
    } catch (err) {
        console.error("Failed to update task:", err);
        alert("Failed to update task. Please try again.");
    }
}

async function deleteTask(id) {
    try {
        const response = await fetch(BASE_URL + "/tasks/" + id, { method: "DELETE" });
        if (!response.ok) throw new Error(await response.text());
        getTasks(); // Refresh the list to remove the deleted task
    } catch (err) {
        console.error("Failed to delete task:", err);
        alert("Failed to delete task. Please try again.");
    }
}
