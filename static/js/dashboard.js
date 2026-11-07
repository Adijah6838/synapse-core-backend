document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    
    if (!token) {
        window.location.href = '/'; // Redirect to login if no token
        return;
    }

    try {
        const response = await fetch('/api/analytics/overview', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();

        if (data.success) {
            // Update Cards
            document.getElementById('stat-users').innerText = data.data.total_users;
            document.getElementById('stat-docs').innerText = data.data.total_documents;
            document.getElementById('stat-active-tasks').innerText = data.data.active_tasks;
            document.getElementById('stat-failed-jobs').innerText = data.data.failed_jobs;

            // Draw Chart
            const ctx = document.getElementById('activityChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Users', 'Documents', 'Active Tasks', 'Completed Tasks', 'Pending Jobs', 'Failed Jobs'],
                    datasets: [{
                        label: 'System Totals',
                        data: [
                            data.data.total_users,
                            data.data.total_documents,
                            data.data.active_tasks,
                            data.data.completed_tasks,
                            data.data.pending_jobs,
                            data.data.failed_jobs
                        ],
                        backgroundColor: [
                            '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#64748b', '#ef4444'
                        ],
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true, ticks: { color: '#94a3b8' } },
                        x: { ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }
    } catch (err) {
        console.error("Failed to load dashboard data", err);
    }
});