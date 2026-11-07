document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    if (!token) window.location.href = '/';

    const docId = 1; // We are hardcoding ID 1 for this test, since it's the one we created
    let currentLockVersion = 0;

    // 1. Fetch the document
    try {
        const res = await fetch(`/api/documents/${docId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        
        if (data.success) {
            document.getElementById('doc-title').innerText = data.data.title;
            document.getElementById('doc-content').value = data.data.content;
            document.getElementById('doc-version').innerText = data.data.current_version;
            currentLockVersion = data.data.lock_version;
        }
    } catch (err) {
        console.error("Error loading doc", err);
    }

    // 2. Save the document
    document.getElementById('save-btn').addEventListener('click', async () => {
        const newContent = document.getElementById('doc-content').value;
        const statusSpan = document.getElementById('save-status');
        
        statusSpan.style.color = '#f59e0b';
        statusSpan.innerText = "Saving...";

        try {
            const res = await fetch(`/api/documents/${docId}`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` 
                },
                body: JSON.stringify({
                    content: newContent,
                    lock_version: currentLockVersion // Send the current version to prevent overwrites
                })
            });
            const data = await res.json();

            if (data.success) {
                statusSpan.style.color = '#10b981';
                statusSpan.innerText = "Saved successfully!";
                currentLockVersion = data.data.lock_version; // Update our version so we can save again
                document.getElementById('doc-version').innerText = data.data.current_version;
                setTimeout(() => statusSpan.innerText = "", 3000);
            } else {
                statusSpan.style.color = '#ef4444';
                statusSpan.innerText = data.message; // Shows the 409 Conflict error if someone else edited it
            }
        } catch (err) {
            console.error("Error saving doc", err);
        }
    });
});