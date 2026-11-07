document.addEventListener('DOMContentLoaded', () => {
    const authForm = document.getElementById('auth-form');
    const toggleBtn = document.getElementById('toggle-auth');
    const formTitle = document.getElementById('form-title');
    const emailGroup = document.getElementById('email-group');
    const submitBtn = document.getElementById('submit-btn');
    const alertBox = document.getElementById('alert-box');
    
    let isLogin = true;

    // Toggle between Login and Register
    toggleBtn.addEventListener('click', () => {
        isLogin = !isLogin;
        if (isLogin) {
            formTitle.innerText = "Login to SYNAPSE";
            emailGroup.style.display = "none";
            submitBtn.innerText = "Login";
            toggleBtn.innerText = "Don't have an account? Register here.";
        } else {
            formTitle.innerText = "Register for SYNAPSE";
            emailGroup.style.display = "block";
            submitBtn.innerText = "Register";
            toggleBtn.innerText = "Already have an account? Login here.";
        }
        alertBox.style.display = 'none';
    });

    // Handle form submission
    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const email = document.getElementById('email').value;

        const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
        const body = isLogin ? { username, password } : { username, email, password };

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await response.json();

            if (data.success) {
                if (isLogin) {
                    // Save token and redirect
                    localStorage.setItem('token', data.data.access_token);
                    alertBox.style.display = 'block';
                    alertBox.style.background = '#10b981';
                    alertBox.style.color = 'white';
                    alertBox.innerText = "Login successful! Redirecting...";
                    setTimeout(() => window.location.href = '/dashboard', 1000);
                } else {
                    alert("Registration successful! Please log in.");
                    toggleBtn.click();
                }
            } else {
                alertBox.style.display = 'block';
                alertBox.style.background = '#ef4444';
                alertBox.style.color = 'white';
                alertBox.innerText = data.message;
            }
        } catch (err) {
            console.error(err);
        }
    });
});