from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from deepface import DeepFace
import base64
from PIL import Image
from io import BytesIO
import os

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('login.html')

def verify_identity(image_path):
    db_path = "img_referencia.jpg" #para probarlo en local se debe tener una imagen de referencia con este nombre
    if not os.path.exists(db_path):
        print(f"Error: no se puede encontrar la imagen de referencia en {db_path}")
        return False, "Imagen de referencia no encontrada"
    
    try:
        verification = DeepFace.verify(img1_path=db_path, img2_path=image_path, model_name='VGG-Face')
        return verification["verified"], "Verificacion completa"
    except Exception as e:
        print(f"Verificacion fallida: {e}")
        return False, str(e)

@socketio.on('image')
def handle_image(json_data):
    image_data = json_data['data']
    header, encoded = image_data.split(",", 1)
    binary_data = base64.b64decode(encoded)
    image = Image.open(BytesIO(binary_data))
    image = image.convert('RGB')
    temp_path = "temp.jpg"
    image.save(temp_path)
    
    is_verified, message = verify_identity(temp_path)
    if is_verified:
        emit('response', {'auth': 'success', 'message': message})
    else:
        emit('response', {'auth': 'fail', 'error': message})

    os.remove(temp_path)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
