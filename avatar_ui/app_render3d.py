from flask import Flask, render_template, send_from_directory,request,url_for,redirect
import os
import sys
# from PIL import Image
from werkzeug.utils import secure_filename
# For chatbot response
from flask import Flask,request,jsonify
from rag import get_chat_response   # Added for chatbot integration


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

@app.route('/get-response', methods=['POST'])

def get_response():
    user_input = request.json.get("message")
    bot_response = get_chat_response(user_input)  
    return jsonify({"response": bot_response})

if __name__ == '__main__':
    app.run(debug=True)


# your_project_root/app.py

# from flask import Flask, render_template, send_from_directory, request, url_for, redirect, jsonify, send_file
# import os
# import io
# # import datetime # No longer needed if time-based response is removed
# # from pytz import timezone # No longer needed if time-based response is removed
# # import pytz # No longer needed if time-based response is removed
# from werkzeug.utils import secure_filename # Make sure this is imported if using secure_filename

# # --- TTS MODEL IMPORTS ---
# # Import your pyttsx3 TTS service instance
# # Ensure tts_pipeline/tts_inference.py is correctly set up as per previous instructions
# from TTS_pipeline.TTS_inference import tts_service_instance 

# # --- Flask App Configuration ---
# app = Flask(__name__, template_folder='templates', static_folder='static')

# # Configuration for avatar uploads
# UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads') # Use app.root_path for robustness
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Configuration for static models (e.g., .glb files for Three.js)
# MODELS_FOLDER = os.path.join(app.root_path, 'static', 'models')
# os.makedirs(MODELS_FOLDER, exist_ok=True) # Ensure models directory exists

# # Ensure an 'audio' directory exists for TTS test files
# AUDIO_FOLDER = os.path.join(app.root_path, 'audio')
# os.makedirs(AUDIO_FOLDER, exist_ok=True)


# # Global list to store avatar metadata
# # In a real application, this would be persisted in a database
# avatars = [] # This list will hold dicts like {'name': '...', 'url': '...'}

# # --- ROUTES ---

# @app.route('/')
# def index():
#     return render_template('index1.html', avatars=avatars)

# # This route serves files from the static/models subdirectory
# @app.route('/static/models/<path:filename>')
# def serve_model(filename):
#     print(f"Flask: Serving model file: {filename} from {MODELS_FOLDER}")
#     return send_from_directory(MODELS_FOLDER, filename)

# @app.route('/upload', methods=['POST'])
# def upload():
#     # Check if 'image' file and 'avatar_name' form data exist
#     if 'image' not in request.files or 'avatar_name' not in request.form:
#         return redirect(url_for('index')) # Redirect back if missing data

#     image = request.files['image']
#     avatar_name = request.form['avatar_name']

#     if image.filename == '':
#         return redirect(url_for('index')) # Redirect if no file selected

#     if image:
#         # Securely save the uploaded image
#         filename = secure_filename(image.filename)
#         image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         image.save(image_path)

#         # Generate the URL for the uploaded avatar
#         avatar_url = url_for('static', filename=f'uploads/{filename}')
        
#         # Add to the global avatars list
#         avatars.append({'name': avatar_name, 'url': avatar_url})
#         print(f"Flask: Uploaded new avatar: Name='{avatar_name}', URL='{avatar_url}'")

#     return redirect(url_for('index'))


# # --- TEXT-TO-SPEECH ROUTE ---
# @app.route('/synthesize-speech', methods=['POST'])
# def synthesize_speech():
#     data = request.get_json()
#     text_to_synthesize = data.get('text', '')

#     if not text_to_synthesize:
#         return jsonify({"error": "No text provided"}), 400

#     # Check if the pyttsx3 service was loaded successfully at app startup
#     if not tts_service_instance.is_loaded:
#         print("Flask Error: TTS service not loaded.")
#         return jsonify({"error": "TTS service not available on server."}), 503 # Service Unavailable

#     try:
#         # Call the pyttsx3 service instance to synthesize audio
#         print(f"Flask: Requesting pyttsx3 synthesis for: '{text_to_synthesize}'")
#         audio_bytes = tts_service_instance.synthesize(text_to_synthesize)
#         print("Flask: pyttsx3 synthesis complete. Sending audio.")
        
#         # Send the audio data back as a WAV file
#         return send_file(
#             io.BytesIO(audio_bytes),
#             mimetype='audio/wav',
#             as_attachment=False, # Do not force download in the browser
#             download_name='synthesized_speech.wav' # Suggested filename for the browser
#         )
#     except Exception as e:
#         print(f"Flask Error during pyttsx3 speech synthesis: {e}")
#         return jsonify({"error": f"Speech synthesis failed: {str(e)}"}), 500

# # --- APP RUN ---
# if __name__ == '__main__':
#     print("hello.....")
#     # Optional: Perform a quick test synthesis on server startup to verify TTS
#     try:
#         if tts_service_instance.is_loaded:
#             print("Flask: Performing a quick pyttsx3 TTS service test on startup...")
#             test_audio = tts_service_instance.synthesize("Hello, this is a server test using pyttsx3.")
#             with open(os.path.join(AUDIO_FOLDER, "server_startup_pyttsx3_test.wav"), "wb") as f:
#                 f.write(test_audio)
#             print(f"Flask: Server startup pyttsx3 TTS test audio saved to {os.path.join(AUDIO_FOLDER, 'server_startup_pyttsx3_test.wav')}")
#         else:
#             print("Flask: pyttsx3 service not loaded, skipping startup test.")
#     except Exception as e:
#         print(f"Flask: Error during pyttsx3 TTS startup test: {e}")

#     app.run(debug=True, port=5000) # Run Flask in debug mode on port 5000