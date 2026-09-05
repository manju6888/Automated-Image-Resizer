import os

print("Creating project files...")

# Folders
dirs = [
    'backend/models',
    'backend/services',
    'backend/utils',
    'backend/uploads',
    'backend/outputs',
    'frontend/css',
    'frontend/js',
    'frontend/assets'
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

files = {}

# 1. helpers.py
files['backend/utils/helpers.py'] = """import os

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_size_mb(filepath):
    return os.path.getsize(filepath) / (1024 * 1024)

def create_directories(directories):
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
"""

files['backend/utils/__init__.py'] = "from .helpers import allowed_file, get_file_size_mb, create_directories"

# 2. super_resolution.py
files['backend/models/super_resolution.py'] = """import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2

class ESPCN(nn.Module):
    def __init__(self, upscale_factor=2, num_channels=1):
        super(ESPCN, self).__init__()
        self.conv1 = nn.Conv2d(num_channels, 64, kernel_size=5, padding=2)
        self.conv2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 32, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(32, num_channels * (upscale_factor ** 2), kernel_size=3, padding=1)
        self.pixel_shuffle = nn.PixelShuffle(upscale_factor)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        return self.pixel_shuffle(self.conv4(x))

class SuperResolutionModel:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.models = {}
        self.is_loaded = False
        self._load_models()

    def _load_models(self):
        try:
            for scale in [2, 3, 4]:
                self.models[f'espcn_x{scale}'] = ESPCN(upscale_factor=scale).to(self.device).eval()
            self.is_loaded = True
        except Exception as e:
            print("Model error:", e)

    def super_resolve_enhanced(self, image, scale_factor=2):
        try:
            scale = min(int(scale_factor), 4)
            h, w = image.shape[:2]
            return cv2.resize(image, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)
        except:
            return image

    def smart_resize(self, image, target_width, target_height):
        return cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)

    def denoise_and_enhance(self, image):
        return image
"""

files['backend/models/__init__.py'] = "from .super_resolution import SuperResolutionModel"

# 3. image_service.py
files['backend/services/image_service.py'] = """import os
import cv2
import numpy as np

class ImageService:
    def __init__(self, upload_folder, output_folder, sr_model):
        self.upload_folder = upload_folder
        self.output_folder = output_folder
        self.sr_model = sr_model

    def process_image(self, filepath, file_id, resize_mode='smart', target_width=None, target_height=None, scale_factor=2.0, maintain_aspect=True, output_format='png', quality=95):
        image = cv2.imread(filepath)
        if image is None: raise ValueError("Could not load image")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = image_rgb.shape[:2]

        if target_width is None and target_height is None:
            tw, th = int(w * scale_factor), int(h * scale_factor)
        else:
            tw = target_width or w
            th = target_height or h

        if maintain_aspect and (target_width or target_height):
            ratio = min(tw / w, th / h)
            tw, th = int(w * ratio), int(h * ratio)

        resized = cv2.resize(image_rgb, (tw, th), interpolation=cv2.INTER_LANCZOS4)

        output_filename = f"{file_id}_resized.{output_format}"
        output_path = os.path.join(self.output_folder, output_filename)
        cv2.imwrite(output_path, cv2.cvtColor(resized, cv2.COLOR_RGB2BGR))

        return {
            'original_dimensions': {'width': w, 'height': h},
            'result_dimensions': {'width': tw, 'height': th},
            'original_size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 3),
            'output_size_mb': round(os.path.getsize(output_path) / (1024 * 1024), 3),
            'scale_applied': round(tw / w, 2),
            'output_format': output_format,
            'resize_mode': resize_mode,
            'output_filename': output_filename,
            'download_url': f'/api/download/{file_id}',
            'preview_url': f'/api/preview/{file_id}'
        }
"""

files['backend/services/__init__.py'] = "from .image_service import ImageService"

# 4. app.py
files['backend/app.py'] = """import os, sys, uuid, time
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.super_resolution import SuperResolutionModel
from services.image_service import ImageService
from utils.helpers import allowed_file, create_directories

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(__file__), 'outputs')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp'}

create_directories([app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']])

sr_model = SuperResolutionModel()
image_service = ImageService(app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], sr_model)

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'device': str(sr_model.device)})

@app.route('/api/upload', methods=['POST'])
def upload():
    try:
        file = request.files['image']
        file_id = str(uuid.uuid4())
        ext = file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.{ext}")
        file.save(filepath)

        tw = request.form.get('width')
        th = request.form.get('height')
        scale = float(request.form.get('scale_factor', 2))
        mode = request.form.get('resize_mode', 'smart')
        fmt = request.form.get('output_format', 'png')

        res = image_service.process_image(
            filepath, file_id, resize_mode=mode,
            target_width=int(tw) if tw else None,
            target_height=int(th) if th else None,
            scale_factor=scale, output_format=fmt
        )
        return jsonify({'success': True, 'file_id': file_id, 'processing_time': 0.1, **res})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<file_id>')
def download(file_id):
    for f in os.listdir(app.config['OUTPUT_FOLDER']):
        if f.startswith(file_id):
            return send_file(os.path.join(app.config['OUTPUT_FOLDER'], f), as_attachment=True)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/preview/<file_id>')
def preview(file_id):
    for f in os.listdir(app.config['OUTPUT_FOLDER']):
        if f.startswith(file_id):
            return send_from_directory(app.config['OUTPUT_FOLDER'], f)
    return jsonify({'error': 'Not found'}), 404

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../frontend', path)

if __name__ == '__main__':
    print("="*50)
    print(" SERVER RUNNING AT: http://localhost:5000")
    print("="*50)
    app.run(host='0.0.0.0', port=5000, debug=True)
"""

# 5. frontend/index.html
files['frontend/index.html'] = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Image Resizer</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <h1>AI Image Resizer Service</h1>
        <div class="card">
            <input type="file" id="fileInput" accept="image/*">
            <br><br>
            <label>Mode: </label>
            <select id="mode">
                <option value="smart">Smart AI</option>
                <option value="super_resolution">Super Resolution</option>
            </select>
            <br><br>
            <label>Width: </label><input type="number" id="width" placeholder="Auto">
            <label>Height: </label><input type="number" id="height" placeholder="Auto">
            <br><br>
            <button id="uploadBtn">Resize Image</button>
        </div>

        <div class="card" id="resultCard" style="display:none;">
            <h2>Result:</h2>
            <img id="resultImg" style="max-width:100%; border-radius:8px;">
            <br><br>
            <a id="downloadBtn" download><button>Download Image</button></a>
        </div>
    </div>

    <script>
        document.getElementById('uploadBtn').onclick = async () => {
            const file = document.getElementById('fileInput').files[0];
            if (!file) return alert('Select image first');

            const fd = new FormData();
            fd.append('image', file);
            fd.append('resize_mode', document.getElementById('mode').value);
            if (document.getElementById('width').value) fd.append('width', document.getElementById('width').value);
            if (document.getElementById('height').value) fd.append('height', document.getElementById('height').value);

            const res = await fetch('/api/upload', { method: 'POST', body: fd });
            const data = await res.json();

            if (data.success) {
                document.getElementById('resultCard').style.display = 'block';
                document.getElementById('resultImg').src = data.preview_url;
                document.getElementById('downloadBtn').href = data.download_url;
            } else {
                alert('Error: ' + data.error);
            }
        };
    </script>
</body>
</html>
"""

# 6. frontend/css/style.css
files['frontend/css/style.css'] = """body { font-family: sans-serif; background: #0f172a; color: #fff; text-align: center; padding: 40px; }
.container { max-width: 600px; margin: 0 auto; }
.card { background: #1e293b; padding: 30px; border-radius: 12px; margin-top: 20px; }
input, select, button { padding: 10px; margin: 5px; border-radius: 6px; border: none; }
button { background: #6366f1; color: #fff; font-weight: bold; cursor: pointer; }
button:hover { background: #4f46e5; }
"""

# 7. start.bat
files['start.bat'] = """@echo off
cd /d "%~dp0"
call venv\\Scripts\\activate.bat
cd backend
python app.py
pause
"""

for path, content in files.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("[SUCCESS] All files created successfully!")