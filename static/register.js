document.getElementById("registerForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Sayfanın yenilenmesini önler

    // Form alanlarındaki verileri al
    let firstname = document.getElementById("firstname").value;
    let lastname = document.getElementById("lastname").value;
    let email = document.getElementById("email").value;
    let usertype = document.getElementById("usertype").value;
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    // Verileri bir JSON nesnesine dönüştür
    let data = {
        firstname: firstname,
        lastname: lastname,
        email: email,
        usertype: usertype,
        username: username,
        password: password
    };

    // Verileri sunucuya gönder
    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            document.getElementById("registerResult").innerText = data.message;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById("registerResult").innerText = "Bir hata oluştu.";
    });
});
