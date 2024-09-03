function register(event) {
    event.preventDefault();  // Formun submit olayını durdur
    
    const formData = {
        firstname: document.getElementById('firstname').value,
        lastname: document.getElementById('lastname').value,
        username: document.getElementById('username').value,
        usertype: document.getElementById('usertype').value,
        password: document.getElementById('password').value,
        email: document.getElementById('email').value
    };

    fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('registerResult').textContent = data.message;
        if (data.message === "Kullanıcı başarıyla kaydedildi!") {
            // Kayıt başarılıysa, kullanıcıyı login sayfasına yönlendirebiliriz
            window.location.href = '/login';
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Form submit olayını dinle
document.getElementById('registerForm').addEventListener('submit', register);
