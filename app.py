from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename
import zipfile
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
# Remove the MAX_CONTENT_LENGTH limit
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # This line is now removed

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'File uploaded successfully', 200

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@app.route('/upload_folder', methods=['POST'])
def upload_folder():
    if 'folder' not in request.files:
        return 'No folder part', 400
    files = request.files.getlist('folder')
    if not files or files[0].filename == '':
        return 'No selected folder', 400
    
    folder_name = secure_filename(request.form.get('folder_name', 'uploaded_folder'))
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    os.makedirs(folder_path, exist_ok=True)

    for file in files:
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(folder_path, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
    
    return 'Folder uploaded successfully', 200

@app.route('/download_folder/<folder_name>')
def download_folder(folder_name):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
    if not os.path.exists(folder_path):
        return 'Folder not found', 404

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file), 
                           os.path.relpath(os.path.join(root, file), folder_path))
    
    memory_file.seek(0)
    return send_file(memory_file, mimetype='application/zip', 
                     as_attachment=True, attachment_filename=f'{folder_name}.zip')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969, debug=True)