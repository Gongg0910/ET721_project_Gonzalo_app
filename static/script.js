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



/* -------------------------------------------------------------- blogs.html -------------------------------------------------------------- */
function Inline_editing(blog_id) {
    const card = document.querySelector(`#blog_card${blog_id}`);
    const paragraph = card.querySelector('.blog_content');
    const old_text = paragraph.textContent;

    const textarea = document.createElement('textarea');
    textarea.classList.add('edit_field');
    textarea.value = old_text;
    textarea.style.width = "100%";
    textarea.style.height = "80px";
    textarea.style.margin = "10px 0";

    // row
    const buttonRow = document.createElement('div');
    buttonRow.classList.add('edit_row');

    // save button
    const saving = document.createElement('button');
    saving.textContent = "Save Changes";
    saving.classList.add('btn_save');
    saving.onclick = () => {

        const updatedText = textarea.value.trim();

        fetch(`/edit_blog/${blog_id}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: updatedText })
        })
        .then(res => {
            /* To load after saving instead of refreshing website */
            if (res.ok) {
                window.location.reload();
            }
        });
    };

    // cancel button
    const canceling = document.createElement('button');
    canceling.textContent = "Cancel";
    canceling.classList.add('btn_cancel');
    canceling.onclick = () => {
        card.replaceChild(paragraph, textarea);
        buttonRow.remove(); 
    };

    buttonRow.appendChild(saving);
    buttonRow.appendChild(canceling);

    card.replaceChild(textarea, paragraph);
    
    textarea.insertAdjacentElement('afterend', buttonRow);
}

function click_for_likes(blog_id) {
    fetch(`/like_blog/${blog_id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const countSpan = document.querySelector(`#like_counting${blog_id}`);
            /* Continue to like more */
            if (countSpan) {
                countSpan.textContent = data.likes;
            }
        } 
    })
}
/* -------------------------------------------------------------- blogs.html -------------------------------------------------------------- */


/* -------------------------------------------------------------- image.html -------------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
    const upload_form = document.querySelector('#upload_form');
    if (upload_form) {
        upload_form.addEventListener('submit', function(e) {
            e.preventDefault();
            const fileInput = document.querySelector('#file_input');
            const message = document.querySelector('#message');
            
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            message.textContent = "Uploading...";
            message.style.color = "orange";
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    message.textContent = data.message;
                    message.style.color = "green";
                    fileInput.value = ""; 
                    setTimeout(() => { window.location.reload(); }, 1000);
                } 
                else {
                    message.textContent = data.error || "Upload failed";
                    message.style.color = 'red';
                }
            })
        });
    }
});

function delete_image(id) {
    /* alert user asking if you are sure to delete image */
    if (!confirm("Are you sure you want to delete this image?")) return;
    
    fetch(`/delete_image_file/${id}`, { method: 'DELETE' })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            const imageCard = document.getElementById(`image_s${id}`);
            if (imageCard) imageCard.remove();
        } 
        else {
            alert(data.error || "Failed to delete image.");
        }
    })
}
/* -------------------------------------------------------------- image.html -------------------------------------------------------------- */