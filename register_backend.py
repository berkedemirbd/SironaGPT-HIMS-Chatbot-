from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# MySQL veritabanı bağlantı bilgileri
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:930343Bd*@localhost:3306/SYS'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '***'  # Flask session'ları şifrelemek için secret key

db = SQLAlchemy(app)

# Kullanıcı modelini oluşturma
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    mail = db.Column(db.String(120), unique=True)
    usertype = db.Column(db.String(50))

    def __init__(self, firstname, lastname, username, password, mail, usertype):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password = password  # Varsayılan hash yöntemi kullanılır
        self.mail = mail
        self.usertype = usertype

# Veritabanını oluştur
with app.app_context():
    db.create_all()

# Ana sayfayı register sayfasına yönlendir
@app.route('/')
def home():
    return redirect(url_for('register'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            if not username or not password:
                return jsonify({"message": "Kullanıcı adı ve şifre gereklidir."}), 400

            user = User.query.filter_by(username=username).first()
            if user and user.password == password:  # Düz metin şifre karşılaştırması
                session['user_id'] = user.id
                session['username'] = user.username
                session['firstname'] = user.firstname
                return redirect("http://127.0.0.1:5000/") # Başarılı girişte yönlendirme
            else:
                return jsonify({"message": "Kullanıcı adı veya şifre yanlış!"}), 401
        return render_template('login.html')
    except Exception as e:
        return jsonify({"message": "Sunucuda bir hata oluştu.", "error": str(e)}), 500


# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        new_user = User(
            firstname=data['firstname'],
            lastname=data['lastname'],
            username=data['username'],
            password=data['password'],
            mail=data['email'],
            usertype=data['usertype']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Kullanıcı başarıyla kaydedildi!"})
    return render_template('register.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
