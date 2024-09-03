from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from langchain_openai import ChatOpenAI  # OpenAI yerine ChatOpenAI kullanıyoruz
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langdetect import detect  # Dil tespiti için langdetect kütüphanesi

app = Flask(__name__)
app.secret_key = '***'  # Flask session'ları şifrelemek için secret key

# MySQL veritabanı bağlantı bilgileri
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:930343Bd*@localhost:3306/SYS'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
        self.password = password  # Düz metin şifre
        self.mail = mail
        self.usertype = usertype

# Veritabanını oluştur
with app.app_context():
    db.create_all()

# GPT-4 modelini kullanacak şekilde ChatOpenAI nesnesi oluşturma
API_KEY = "***"
llm = ChatOpenAI(temperature=0.7, api_key=API_KEY, model="gpt-3.5-turbo")
embeddings = OpenAIEmbeddings(openai_api_key=API_KEY)

def load_and_split_document(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Dökümanı parçalara ayırma
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=0)
    texts = text_splitter.split_text(text)

    # Chunklara meta veri ekleyerek döküman objeleri oluşturma
    docs = [Document(page_content=t, metadata={"source": f"chunk_{i}"}) for i, t in enumerate(texts)]
    return docs

documents = load_and_split_document("egitim.txt")

# Vektör deposunu ve retriever'ı oluşturma
vector_store = FAISS.from_documents(documents, embeddings)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# RetrievalQA chain oluşturma
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# Ana sayfayı login sayfasına yönlendir
@app.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            session.clear()
            username = request.form.get('username')
            password = request.form.get('password')
            if not username or not password:
                return jsonify({"message": "Kullanıcı adı ve şifre gereklidir."}), 400

            user = User.query.filter_by(username=username).first()
            if user and user.password == password:  # Düz metin şifre karşılaştırması
                session['user_id'] = user.id
                session['username'] = user.username
                session['firstname'] = user.firstname
                session['usertype'] = user.usertype
                return redirect("http://127.0.0.1:5000/")  # Başarılı girişte yönlendirme
            else:
                return jsonify({"message": "Kullanıcı adı veya şifre yanlış!"}), 401
        return render_template('login.html')
    except Exception as e:
        return jsonify({"message": "Sunucuda bir hata oluştu.", "error": str(e)}), 500


@app.route("/send_message", methods=["POST"])
def send_message():
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    if 'user_id' in session:
        firstname = session['firstname']
        usertype = session.get('usertype', 'yetkisiz')  # Usertype session'dan alınıyor
        print(f"Kullanıcı adı: {firstname}, Kullanıcı tipi: {usertype}")  # Debugging için yazdırıyoruz
    else:
        return jsonify({"error": "Kullanıcı oturumu yok."}), 401

    if 'yetki' in user_message.lower():
        return jsonify({
            "message": "Maalesef yetki konularında yardımcı olamıyorum. Lütfen bilgi işlem birimine veya HSS çalışanına danışınız."
        }), 200

    if 'parametre ayar' in user_message.lower():  # Bu koşul çalışıyor mu kontrol et
        print(f"Parametre ayarları mesajı alındı. Kullanıcı tipi: {usertype}")  # Debugging için yazdırıyoruz

        if usertype == "user1":
            return jsonify({
                "message": "Maalesef kullanıcınız 'yetkisiz' olarak tanımlanmış. Parametre ayarlarını ellemeyiniz."
            }), 200

        elif usertype == "user2":
            return jsonify({
                "message": "Standart kullanıcı yetkisine sahipsiniz. Standart yetkiye sahip kullanıcılar parametre ayarlarını maalesef yapılandıramazlar."
            }), 200

        else:
            return jsonify({
                "message": "Admin yetkisine sahipsiniz parametre ayarlarını yapılandırabiliyor olmanız gerek. Eğer bir yanlışlık olduğunu düşünüyorsanız bilgi işleme bildiriniz."
            }), 200

    if 'selam' in user_message.lower() or 'merhaba' in user_message.lower():
        return jsonify({
            "message": f"Merhaba {firstname}, sana nasıl yardımcı olabilirim?"
        }), 200

    if 'naber' in user_message.lower():
        return jsonify({
            "message": f"iyi bro sen"
        }), 200

    # Kullanıcı mesajını sorgu olarak işleme
    prompt = "Lütfen sadece Türkçe dilinde yanıt ver. Soru: " + user_message
    try:
        response = qa_chain.invoke({"query": prompt})
        detected_language = detect(response["result"])
        if detected_language != "tr":
            return jsonify({"message": "Üzgünüm, sadece Türkçe dilinde yanıt verebilirim."}), 200

        return jsonify({
            "message": response["result"],
            "source_documents": [doc.metadata["source"] for doc in response["source_documents"]]
        }), 200
    except Exception as e:
        return jsonify({"error": f"API çağrısı başarısız oldu: {str(e)}"}), 500


@app.route('/logout')
def logout():
    session.clear()  # Oturumdaki tüm verileri temizle
    return redirect(url_for('login'))  # Kullanıcıyı login sayfasına yönlendir


if __name__ == "__main__":
    app.run(debug=False)
