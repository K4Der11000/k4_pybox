from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import os
import shutil
import requests

app = Flask(__name__)
app.secret_key = 'secret-key'

UPLOAD_FOLDER = 'uploads'
STATIC_V86 = os.path.join('static', 'v86')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PASSWORD = "kader11000"

@app.before_first_request
def auto_install_v86():
    if not os.path.exists(os.path.join(STATIC_V86, "v86.js")):
        try:
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
                r = requests.get(url)
                r.raise_for_status()
                with open(local_path, 'wb') as f:
                    f.write(r.content)
            print("v86 installed successfully.")
        except Exception as e:
            print(f"Failed to install v86: {e}")

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

    if not iso or not iso.filename.endswith('.iso'):
        flash("Please select a valid ISO file.")
        return redirect(url_for('index'))

    iso_path = os.path.join(UPLOAD_FOLDER, iso.filename)
    iso.save(iso_path)

    return render_template("run_vm.html", iso_file=iso.filename, ram_mb=ram_mb)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

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
        r = requests.get(url)
        with open(local_path, 'wb') as f:
            f.write(r.content)

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
