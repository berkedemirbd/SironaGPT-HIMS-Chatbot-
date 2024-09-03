function login() {
    const formData = {
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
    };

    fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loginResult').textContent = data.message;
        if (data.message === "Giriş başarılı!") {
            // Giriş başarılıysa, kullanıcıyı ana sayfaya yönlendirebilirsiniz
            window.location.href = '/';
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function goToRegister() {
    window.location.href = 'register.html';  // Register sayfasına yönlendirme
}

// 'Register' butonuna event listener ekleme
document.querySelector('.register').addEventListener('click', goToRegister);
