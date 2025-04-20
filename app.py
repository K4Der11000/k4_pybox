from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import os
import shutil
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret-key'  # يُفضل تغييره إلى قيمة عشوائية طويلة

# إعدادات المسارات
UPLOAD_FOLDER = 'uploads'
STATIC_V86 = os.path.join('static', 'v86')
ALLOWED_EXTENSIONS = {'iso'}
MAX_CONTENT_LENGTH = 1 * 1024 * 1024 * 1024  # 1 GB max upload

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# كلمة المرور للدخول
PASSWORD = "kader11000"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            flash("Incorrect password.")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route('/run', methods=['POST'])
def run():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    iso = request.files.get('iso_file')
    ram_mb = request.form.get('ram_mb', 256)

    if not iso or not allowed_file(iso.filename):
        flash("Please select a valid ISO file.")
        return redirect(url_for('index'))

    filename = secure_filename(iso.filename)
    iso_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    iso.save(iso_path)

    return render_template("run_vm.html", iso_file=filename, ram_mb=ram_mb)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/install_v86')
def install_v86():
    os.makedirs(STATIC_V86, exist_ok=True)

    files = {
        "v86.js": "https://copy.sh/v86/build/v86.js",
        "v86.wasm": "https://copy.sh/v86/build/v86.wasm",
        "bios/seabios.bin": "https://copy.sh/v86/bios/seabios.bin",
        "bios/vgabios.bin": "https://copy.sh/v86/bios/vgabios.bin",
    }

    for path, url in files.items():
        local_path = os.path.join(STATIC_V86, path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        try:
            r = requests.get(url)
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                f.write(r.content)
        except Exception as e:
            flash(f"Error downloading {path}: {e}")
            return redirect(url_for('index'))

    flash("v86 Emulator installed successfully!")
    return redirect(url_for('index'))

@app.route('/delete_v86')
def delete_v86():
    if os.path.exists(STATIC_V86):
        shutil.rmtree(STATIC_V86)
    flash("v86 files deleted.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
