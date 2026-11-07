document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/';
        return;
    }

    const workspaceId = 1; 
    const taskList = document.getElementById('task-list');
    const newTaskForm = document.getElementById('new-task-form');
    const btnNewTask = document.getElementById('btn-new-task');

    // Toggle form visibility
    btnNewTask.addEventListener('click', () => {
        if (newTaskForm.style.display === 'none') {
            newTaskForm.style.display = 'block';
        } else {
            newTaskForm.style.display = 'none';
        }
    });

    // Load tasks
    const loadTasks = async () => {
        taskList.innerHTML = '<p>Loading tasks...</p>';
        try {
            const res = await fetch(`/api/workspaces/${workspaceId}/tasks`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            
            taskList.innerHTML = '';
            if (data.success && data.data.length > 0) {
                data.data.forEach(task => {
                    const div = document.createElement('div');
                    div.className = 'card';
                    div.style.padding = '1rem';
                    div.style.marginBottom = '0';
                    div.innerHTML = `
                        <div style="display: flex; justify-content: space-between;">
                            <strong>${task.title}</strong>
                            <span style="color: #3b82f6; font-size: 0.8rem; border: 1px solid #3b82f6; padding: 2px 6px; border-radius: 4px;">${task.priority}</span>
                        </div>
                        <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.5rem;">Status: ${task.status}</div>
                    `;
                    taskList.appendChild(div);
                });
            } else {
                taskList.innerHTML = '<p style="color: #94a3b8;">No tasks yet. Create one!</p>';
            }
        } catch (err) {
            console.error("Error loading tasks", err);
        }
    };

    // Create task
    document.getElementById('save-task-btn').addEventListener('click', async () => {
        const title = document.getElementById('task-title').value;
        const priority = document.getElementById('task-priority').value;
        
        if (!title) return alert("Title is required");

        try {
            await fetch(`/api/workspaces/${workspaceId}/tasks`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` 
                },
                body: JSON.stringify({ title, priority })
            });

            newTaskForm.style.display = 'none';
            document.getElementById('task-title').value = '';
            loadTasks(); 
        } catch (err) {
            console.error("Error saving task", err);
        }
    });

    loadTasks();
});