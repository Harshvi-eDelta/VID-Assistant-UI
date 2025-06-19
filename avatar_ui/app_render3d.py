from flask import Flask, render_template, send_from_directory,request,url_for,redirect
import os
import sys
# from PIL import Image
from werkzeug.utils import secure_filename
# For chatbot response
from flask import Flask,request,jsonify
# from rag import get_chat_response   # Added for chatbot integration


app = Flask(__name__)
UPLOAD_FOLDER = 'avatar_ui/static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Get all uploaded avatars and their names
avatars = []    

@app.route('/')
def index():
    return render_template('index1.html',avatars=avatars)

STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app.config['STATIC_FOLDER'] = STATIC_FOLDER

os.makedirs(os.path.join(STATIC_FOLDER, 'models'), exist_ok=True)

# This route serves ANY file from the static/models subdirectory, including .glb
@app.route('/static/models/<path:filename>')
def serve_model(filename):
    print(f"Serving model file: {filename}")
    return send_from_directory(os.path.join(STATIC_FOLDER, 'models'), filename)

@app.route('/upload', methods=['POST'])

def upload():
    image = request.files['image']
    avatar_name = request.form['avatar_name']

    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        avatar_url = url_for('static', filename=f'uploads/{filename}')
        avatars.append({'name': avatar_name, 'url': avatar_url})

    return redirect(url_for('index'))

# @app.route('/get-response', methods=['POST'])

# def get_response():
    # user_input = request.json.get("message")
    # bot_response = get_chat_response(user_input)  
    # return jsonify({"response": bot_response})

if __name__ == '__main__':
    app.run(debug=True)

