from flask import Flask, render_template, send_from_directory,request,url_for,redirect,send_file,Response
import os
import sys
import io
import datetime
from werkzeug.utils import secure_filename
from flask import Flask,request,jsonify
from avatar_ui.TTS_pipeline import TTS_inference
# from TTS.api import TTS
from gtts import gTTS

# For chatbot response
from Chatbot.Final_generate import get_bot_response
import json 


from flask import Flask, render_template, send_from_directory, request, url_for, jsonify
import os
import shutil
import subprocess
from werkzeug.utils import secure_filename
import traceback
import trimesh
import pyrender
import numpy as np
from PIL import Image

app = Flask(__name__)

# ---------- Folders ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'uploads')
MODEL_FOLDER = os.path.join(STATIC_FOLDER, 'models')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MODEL_FOLDER'] = MODEL_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)

# ---------- Homepage ----------
@app.route('/')
def index():
    selected = request.args.get('selected', default=None)
    avatar_files = os.listdir(app.config['UPLOAD_FOLDER'])
    avatars = []

    for fname in avatar_files:
        if fname.lower().endswith('.png'):
            base_name = os.path.splitext(fname)[0]
            glb_path = os.path.join(app.config['MODEL_FOLDER'], f"{base_name}.glb")
            if os.path.exists(glb_path):
                avatars.append({
                    'name': base_name,
                    'url': url_for('static', filename=f"uploads/{base_name}.png")
                })

    return render_template('index1.html', avatars=avatars, selected_avatar_name=selected)

# ---------- Serve .glb files ----------
@app.route('/static/models/<path:filename>')
def serve_model(filename):
    file_path = os.path.join(app.config['MODEL_FOLDER'], filename)
    if not os.path.exists(file_path):
        print(f"[ERROR] Model file not found: {file_path}")
    else:
        print(f"[INFO] Serving model file: {file_path}")
    return send_from_directory(app.config['MODEL_FOLDER'], filename)

# ---------- GLB → PNG ----------
def render_glb_to_png(glb_path, output_png_path):
    try:
        scene_or_mesh = trimesh.load(glb_path)

        # Convert to pyrender.Scene
        scene = pyrender.Scene()
        if isinstance(scene_or_mesh, trimesh.Trimesh):
            mesh = pyrender.Mesh.from_trimesh(scene_or_mesh)
            scene.add(mesh)
        elif isinstance(scene_or_mesh, trimesh.Scene):
            for geometry in scene_or_mesh.geometry.values():
                mesh = pyrender.Mesh.from_trimesh(geometry)
                scene.add(mesh)
        else:
            raise ValueError("Invalid GLB input format.")

        # Render using OffscreenRenderer
        renderer = pyrender.OffscreenRenderer(viewport_width=512, viewport_height=512)
        color, _ = renderer.render(scene)
        renderer.delete()

        img = Image.fromarray(color)
        img.save(output_png_path)
        print(f"[INFO] Rendered PNG saved at: {output_png_path}")

    except Exception as e:
        print(f"[ERROR] Failed to render GLB to PNG: {e}")
        traceback.print_exc()
        raise

# ---------- Upload & Generate Avatar ----------
@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'image' not in request.files:
            return jsonify({'status': 'error', 'message': 'No image uploaded'}), 400

        image = request.files['image']
        avatar_name = request.form.get('avatar_name', 'avatar').strip()

        if image.filename == '' or not avatar_name:
            return jsonify({'status': 'error', 'message': 'Missing file or name'}), 400

        base_name = secure_filename(avatar_name)
        ext = os.path.splitext(image.filename)[-1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            return jsonify({'status': 'error', 'message': 'Unsupported file type'}), 400

        filename = base_name + ext
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(saved_path)

        FACEVERSE_PATH = "/Users/edelta076/Desktop/Project_VID_Assistant4/FaceVerse_v4"
        RUN_SCRIPT = "run.py"
        CONFIG_YML = "configs/faceverse.yml"
        MESH_SCRIPT = "scripts/3d_mesh.py"

        # Step 1
        subprocess.run(
            f"cd {FACEVERSE_PATH} && ./faceverse_cpu_env/bin/python {RUN_SCRIPT} --cfg {CONFIG_YML} --input {saved_path}",
            shell=True,
            check=True
        )

        # Step 2
        subprocess.run(
            f"cd {FACEVERSE_PATH} && ./faceverse_cpu_env/bin/python {MESH_SCRIPT} --name {base_name}",
            shell=True,
            check=True
        )

        # Step 3
        source_glb = os.path.join(FACEVERSE_PATH, "results", f"{base_name}.glb")
        target_glb = os.path.join(app.config['MODEL_FOLDER'], f"{base_name}.glb")
        shutil.copyfile(source_glb, target_glb)

        source_jpg = os.path.join(FACEVERSE_PATH, "results", f"{base_name}.jpg")
        target_jpg = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}.jpg")
        shutil.copyfile(source_jpg, target_jpg)

        # Step 4: Render PNG using render_glb.py
        output_png_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}.png")
        subprocess.run(
            ['python', os.path.join(BASE_DIR, 'render_glb.py'),
            '--input', target_glb,
            '--output', output_png_path],
            check=True
        )

        return jsonify({
            'status': 'success',
            'avatar_name': base_name,
            'glb_url': f"/static/models/{base_name}.glb",
            'jpg_url': f"/static/uploads/{base_name}.jpg",  # Optional
            'png_url': f"/static/uploads/{base_name}.png"
        })

    except subprocess.CalledProcessError as e:
        print("[ERROR] Subprocess failed:", e)
        return jsonify({'status': 'error', 'message': f'Subprocess error: {e}'}), 500
    except Exception as e:
        print("[ERROR] Upload failed:", e)
        return jsonify({'status': 'error', 'message': f'Unexpected error: {e}'}), 500

custom=True
@app.route('/synthesize-speech', methods=['POST'])
def synthesize_speech():
    try:
        data = request.get_json(silent=True)
        print("Flask: Received json for TTS:",data)
        if data is None:
            print("Flask Request: Body is not valid JSON or is empty.")
            return jsonify({"error": "Invalid JSON or empty body provided"}), 400

        text = data.get('text')
            
        if not text:
            print("Flask Request: 'text' field missing from JSON payload.")
            return jsonify({"error": "No text provided in JSON payload"}), 400
        
        if custom:
            audio_bytes = TTS_inference.tts_model_instance.synthesize(text)
            # return Response(audio_bytes, mimetype="audio/wav")
            return Response(audio_bytes)
        else:
            tts1 = gTTS(text, lang='en')
            current_datetime = datetime.datetime.now()
            current_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            audio_path=f"static/audio/{current_datetime}.wav"
            tts1.save(f"avatar_ui/{audio_path}")
            print(f"backend TTS: saved audio file {audio_path}")
            return Response(audio_path)

    except Exception as e:
        print(f"Flask Error during TTS synthesis: {e}")
        import traceback
        traceback.print_exc() 
        return jsonify({"error": str(e)}), 500

@app.route('/get-response', methods=['POST'])
def get_response():
    data = request.get_json()
    print(f">> Flask received input: {data}")
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please enter something."})

    # Call your chatbot logic
    response = get_bot_response(user_message)
    return jsonify({"response": response})


# ---------- Main ----------
if __name__ == '__main__':
    app.run(debug=True)



