import os
import cv2
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DB_FILE = 'images.db'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ------------------------
# Inicializar o banco SQLite
# ------------------------
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                processed_filename TEXT,
                upload_time TEXT,
                ip_address TEXT
            )
        ''')
        conn.commit()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return render_template('index.html', error='Nenhuma imagem foi enviada.')

    image = request.files['image']
    filename = secure_filename(image.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(filepath)

    # Processamento com Canny
    img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    edges = cv2.Canny(img, 100, 200)
    processed_filename = 'processed_' + filename
    processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
    cv2.imwrite(processed_path, edges)

    # Salvar no banco
    upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip = request.remote_addr

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO images (filename, processed_filename, upload_time, ip_address)
            VALUES (?, ?, ?, ?)
        ''', (filename, processed_filename, upload_time, ip))
        conn.commit()

    return render_template('index.html',
                           original_image=filename,
                           processed_image=processed_filename,
                           ip=ip,
                           datetime=upload_time)

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_image(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    processed_filename = 'processed_' + filename
    processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)

    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM images WHERE filename = ?', (filename,))
            conn.commit()

        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(processed_path):
            os.remove(processed_path)

        print(f'[OK] Arquivos deletados: {file_path}, {processed_path}')
        return jsonify({'message': f'{filename} deletado com sucesso.'}), 200
    except Exception as e:
        print(f'[ERRO] Falha ao deletar {filename}: {e}')
        return jsonify({'error': 'Erro ao deletar o arquivo.'}), 500

@app.route('/image/<filename>')
def uploaded_file(filename):
    file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
