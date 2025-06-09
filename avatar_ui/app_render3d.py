from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app.config['STATIC_FOLDER'] = STATIC_FOLDER

os.makedirs(os.path.join(STATIC_FOLDER, 'models'), exist_ok=True)

@app.route('/')
def index():
    return render_template('index1.html')

# This route serves ANY file from the static/models subdirectory, including .glb
@app.route('/static/models/<path:filename>')
def serve_model(filename):
    print(f"Serving model file: {filename}")
    return send_from_directory(os.path.join(STATIC_FOLDER, 'models'), filename)

if __name__ == '__main__':
    app.run(debug=True)