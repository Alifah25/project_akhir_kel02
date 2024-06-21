import os
from flask import Flask, jsonify, render_template, redirect, url_for, request, session
import hashlib
from werkzeug.utils import secure_filename

from pymongo import MongoClient

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['UPLOAD_FOLDER'] = 'static/dokumen'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

students = []


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/homeuser')
def homeuser():
    return render_template('home.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST" :
        email_receive = request.form["email_give"]
        pw_receive = request.form["pw_give"]

        pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()

        findUser = db.user.find_one({"email": email_receive, "pw": pw_hash})
        
        if findUser:
            session['user'] = email_receive
            return jsonify({"result": "success"})
        else :
            return jsonify({"result": "error"})

    return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST" :
        email_receive = request.form["email_give"]
        pw_receive = request.form["pw_give"]
        name_receive = request.form["name_give"]
        
        pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()

        findEmail = db.user.find_one({"email": email_receive})

        if findEmail:
            return jsonify({"result": "error"})

        else:
            db.user.insert_one({"name" : name_receive, "email": email_receive, "pw": pw_hash})

    return render_template('register.html')

@app.route('/pengumuman')
def pengumuman():
    return render_template('pengumuman.html')

@app.route('/profile', methods=["GET", "POST"])
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        nama_receive = request.form["nama_give"]
        gender_receive = request.form["gender_give"]
        alamat_receive = request.form["alamat_give"]
        tempatLahir_receive = request.form["tempatLahir_give"]
        tanggalLahir_receive = request.form["tanggalLahir_give"]

        if 'foto_give' in request.files:
            foto_receive = request.files["foto_give"]
            foto_path = f"static/profile_pics/{foto_receive.filename}"
            foto_receive.save(foto_path)
        else:
            foto_path = "static/profile_pics/profile_placeholder.jpeg"

        doc = {
            "nama": nama_receive,
            "gender": gender_receive,
            "alamat": alamat_receive,
            "tempatLahir": tempatLahir_receive,
            "tanggalLahir": tanggalLahir_receive,
            "email": session['user'],
            "foto": foto_path
        }

        profile = db.profile.find_one({"email": session['user']})

        if profile:
            db.profile.update_one(
                {"email": session['user']},
                {"$set": {
                    "nama": nama_receive,
                    "gender": gender_receive,
                    "alamat": alamat_receive,
                    "tempatLahir": tempatLahir_receive,
                    "tanggalLahir": tanggalLahir_receive,
                    "foto": foto_path
                }}
            )
        else:
            db.profile.insert_one(doc)
        return jsonify({"result": "success"})

    profile = db.profile.find_one({"email": session['user']})

    if profile:
        user_info = {
            "nama": profile.get('nama', ''),
            "gender": profile.get('gender', ''),
            "alamat": profile.get('alamat', ''),
            "tempatLahir": profile.get('tempatLahir', ''),
            "tanggalLahir": profile.get('tanggalLahir', ''),
            "foto": profile.get('foto', 'static/profile_pics/profile_placeholder.jpeg')
        }
    else:
        user_info = {
            "nama": '',
            "gender": '',
            "alamat": '',
            "tempatLahir": '',
            "tanggalLahir": '',
            "foto": 'static/profile_pics/profile_placeholder.jpeg'
        }
    return render_template('profile.html', user_info=user_info)

@app.route('/updateprofile', methods=["POST"])
def updateprofile():
    return render_template('profile.html')

@app.route('/pendaftaran')
def daftar():
    return render_template('pendaftaran.html')

#untuk mengirim data pendaftaran
@app.route('/kirim-data', methods=['POST'])
def kirim_data():
    if request.method == 'POST':
        nama_lengkap = request.form['nama_lengkap']
        nama_panggilan = request.form['nama_panggilan']
        asalprovinsi = request.form['asalprovinsi']
        asalkota_kabupaten = request.form['asalkota_kabupaten']
        asaldusun_desa = request.form['asaldusun_desa']
        jenis_kelamin = request.form['jenis_kelamin']
        nomor_hp = request.form['nomor_hp']
        dokumen = request.files['dokumen']

        filename = None
        if dokumen:
            filename = secure_filename(dokumen.filename)
            dokumen_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            os.makedirs(os.path.dirname(dokumen_path), exist_ok=True)
            dokumen.save(dokumen_path)

        student = {
            'nama_lengkap': nama_lengkap,
            'nama_panggilan': nama_panggilan,
            'asalprovinsi': asalprovinsi,
            'asalkota_kabupaten': asalkota_kabupaten,
            'asaldusun_desa': asaldusun_desa,
            'jenis_kelamin': jenis_kelamin,
            'nomor_hp': nomor_hp,
            'dokumen': filename
        }
        db.students.insert_one(student)
        return render_template('home.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run("0.0.0.0", port=5000, debug=True)