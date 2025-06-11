# Backend
from flask import Flask, render_template,send_from_directory,request,url_for,redirect
import os
# from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'avatar_ui/static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Get all uploaded avatars and their names
avatars = []

@app.route('/')
def index():
    return render_template('index.html', avatars=avatars)

STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app.config['STATIC_FOLDER'] = STATIC_FOLDER

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

if __name__ == '__main__':
    app.run(debug=True)



'''from flask import Flask, render_template, request,send_from_directory
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'avatar_ui/static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html', uploaded_image=None)

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "No file part", 400

    img = request.files['image']
    print(img)
    if img.filename == '':
        return "No selected file", 400

    img_path = os.path.join(app.config['UPLOAD_FOLDER'], img.filename)
    

    try:
        img.save(img_path)
        print(f" File saved at: {img_path}")
    except Exception as e:
        print(f" Failed to save image: {e}")

    abs_path = os.path.abspath(img_path)
    print(f"Absolute save path: {abs_path}")

    # This is the URL path (NOT file path)
    img_url = f"/static/uploads/{img.filename}"
    return render_template('index.html', uploaded_image=img_url)

    # return render_template('index.html', uploaded_image=f"{send_from_directory(app.config['UPLOAD_FOLDER'], img.filename)}")

if __name__ == '__main__':
    app.run(debug=True)'''


# def upload():
#     if 'image' not in request.files:
#         return "No file part", 400

#     img = request.files['image']
#     avatar_name = request.form.get('avatar_name', 'avatar')

#     if img.filename == '':
#         return "No selected file", 400

#     filename = f"{avatar_name}.jpg"  # Save the image with a custom name
#     img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

#     # Resize image to 200x200 to ensure consistency
#     try:
#         image = Image.open(img)
#         image = image.convert("RGB")  # Convert to RGB to handle PNG/JPEG
#         image = image.resize((200, 200))  # Resize to 200x200
#         image.save(img_path)
#         print(f"File saved at: {img_path}")
#     except Exception as e:
#         print(f"Failed to save image: {e}")
#         return "Error saving image", 500

#     # After saving, we return the updated gallery
#     return index()
