/* login.html */
function validatePassword() { 
    const passwordInput = document.querySelector('input[name="password"]'); 
    const password = passwordInput.value; 
    if (password.length < 6) { 
        alert("Password must be at least 6+ characters"); 
        return false; 
    } 
    return true; 
} 

/* -------------------------------------------------------------- index.html -------------------------------------------------------------- */
/* -------------------------- */
/* Load task after adding     */
/* -------------------------- */
document.addEventListener("DOMContentLoaded", () => { 

    if (document.querySelector("#tasklist")) { 
        loadTasks(); 
    } 
    const authForm = document.querySelector('form'); 
    if (authForm && document.querySelector('input[name="password"]')) { 
        authForm.onsubmit = validatePassword; 
    } 
}); 
function loadTasks() { 
    fetch("/get_tasks") 
        .then(response => response.json()) 
        .then(data => { 
            const list = document.querySelector("#tasklist");  
            list.innerHTML = ""; 
            data.forEach(task => { 
                createTaskElement(task.id, task.task, task.completed); 
            }); 
        }) 
        .catch(err => console.error("Error loading tasks:", err)); 
} 


/* -------------------------- */
/* add task                   */
/* -------------------------- */
function addTask() { 
    const input = document.querySelector('#taskinput'); 
    const task = input.value.trim(); 

    fetch("/add_task", { 
        method: "POST", 
        headers: {"Content-Type": "application/json"}, 
        body: JSON.stringify({task: task}) 
    }) 
    .then(response => response.json()) 
    .then(() => { 
        input.value = ""; 
        loadTasks(); 
    }) 
} 

/* -------------------------- */
/* Delete task                */
/* -------------------------- */
function deleteTask(id) { 
    fetch("/delete_task", { 
        method: "POST", 
        headers: {"Content-Type": "application/json"}, 
        body: JSON.stringify({id: id}) 
    }) 
    .then(() => loadTasks()) 
} 


/* ---------------------------------------------------- */
/* Completion and edit and delete for html's looks*/
/* ---------------------------------------------------- */
function createTaskElement(id, taskText, completed){ 
    const list = document.querySelector('#tasklist'); 
    const li = document.createElement("li"); 
    li.classList.add("task-item"); 

    if (completed === 1) { 
        li.classList.add("completed"); 
    } 

    // for completion <input>
    const completion = document.createElement("input"); 
    completion.type = "checkbox"; 
    completion.classList.add("task-checkbox"); 
    completion.checked = (completed === 1); 
    completion.onchange = () => { 
        complete_task(id, completion.checked ? 1 : 0); 
    }; 


    // To edit task item (I remember from Et-712 about onclick)
    const editing = document.createElement("span"); 
    editing.textContent = taskText; 
    editing.classList.add("task-text-clickable"); 
    editing.onclick = () => { 
        const input = document.createElement("input"); 
        input.type = "text"; 
        input.value = editing.textContent.trim(); 
        input.classList.add("task-edit-item"); 

        input.onblur = () => { 
            updating_task(id, input.value); 
        }; 

        li.replaceChild(input, editing); 
        
        input.focus(); 
    }; 


    const deleting = document.createElement("button"); 
    deleting.innerHTML = "❌"; 
    deleting.onclick = () => deleteTask(id); 
    deleting.classList.add("btn-delete-item"); 

    /* To run the program, I remember this technique from c++ */
    li.appendChild(completion); 
    li.appendChild(editing); 
    li.appendChild(deleting); 
    list.appendChild(li); 
}  

function complete_task(id, value) { 
    fetch("/toggle_task", { 
        method: "POST", 
        headers: {"Content-Type": "application/json"}, 
        body: JSON.stringify({id: id, completed: value}) 
    }) 
    .then(() => loadTasks()) 
} 

function updating_task(id, new_text) { 
    if (new_text.trim() === "") return loadTasks(); 
    fetch("/update_task", { 
        method: "POST", 
        headers: {"Content-Type": "application/json"}, 
        body: JSON.stringify({id: id, task: new_text}) 
    }) 
    .then(() => loadTasks()) 
}
/* -------------------------------------------------------------- index.html -------------------------------------------------------------- */
