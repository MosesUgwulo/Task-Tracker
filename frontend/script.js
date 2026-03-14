const BaseURL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
    getTasks();
});

async function getTasks() {
    const response = await fetch(BaseURL + "/tasks");
    const tasks = await response.json();
    const taskList = document.getElementById("task-list");
    let html = "";
    tasks.forEach(task => {
        html += `<div>
            <h3>Name: ${task.name}</h3>
            <p>Description: ${task.description}</p>
            <p>Status: ${task.status}</p>
            <p>Due Date: ${task.due_date}</p>
        </div>`;
        
    });
    taskList.innerHTML = html;
}