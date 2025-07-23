from flask import request, jsonify
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def subir_imagen():
    if 'imagen' not in request.files:
        return jsonify({"error": "No se encontró ninguna imagen"}), 400

    imagen = request.files['imagen']

    if imagen.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    if imagen and allowed_file(imagen.filename):
        filename = secure_filename(imagen.filename)
        ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        imagen.save(ruta)

        # Construir URL pública
        url_imagen = f"http://127.0.0.1:5000/static/uploads/{filename}"
        return jsonify({"url": url_imagen}), 200

    return jsonify({"error": "Extensión de archivo no permitida"}), 400
