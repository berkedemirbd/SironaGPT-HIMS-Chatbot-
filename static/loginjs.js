document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault();  // Sayfanın yenilenmesini önler

    // Form verilerini al
    const formData = new FormData(document.getElementById("loginForm"));

    // Flask sunucusuna verileri gönder
    fetch('http://192.168.0.19:5000/login', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())  // Yanıtı JSON formatında al
    .then(data => {
        if (data.message === "Giriş başarılı!") {
            window.location.href = 'http://127.0.0.1:5000/';  // Giriş başarılıysa anasayfaya yönlendir
        } else {
            throw new Error("Giriş başarısız!");  // Hata durumunda manuel bir hata fırlatıyoruz
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});
