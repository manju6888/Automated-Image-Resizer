import os, sys, uuid, time
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.super_resolution import SuperResolutionModel
from services.image_service import ImageService
from utils.helpers import allowed_file, create_directories

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), 'frontend')

app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(BASE_DIR, 'outputs')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff'}

create_directories([app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']])

sr_model = SuperResolutionModel()
image_service = ImageService(
    app.config['UPLOAD_FOLDER'],
    app.config['OUTPUT_FOLDER'],
    sr_model
)

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'device': str(sr_model.device),
        'model_loaded': sr_model.is_loaded
    })

@app.route('/api/upload', methods=['POST'])
def upload():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        file_id = str(uuid.uuid4())
        ext = file.filename.rsplit('.', 1)[-1].lower()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_original.{ext}")
        file.save(filepath)

        # Read form values
        resize_mode = request.form.get('resize_mode', 'smart')
        scale_factor = float(request.form.get('scale_factor', '2'))
        output_format = request.form.get('output_format', 'png')
        quality = int(request.form.get('quality', '95'))
        maintain_aspect = request.form.get('maintain_aspect', 'true').lower() == 'true'

        tw = request.form.get('width')
        th = request.form.get('height')
        target_width = int(tw) if tw and tw.strip() else None
        target_height = int(th) if th and th.strip() else None

        print(f"\n[UPLOAD] mode={resize_mode} scale={scale_factor} w={target_width} h={target_height}")

        start = time.time()
        result = image_service.process_image(
            filepath=filepath,
            file_id=file_id,
            resize_mode=resize_mode,
            target_width=target_width,
            target_height=target_height,
            scale_factor=scale_factor,
            maintain_aspect=maintain_aspect,
            output_format=output_format,
            quality=quality
        )
        elapsed = round(time.time() - start, 3)

        return jsonify({
            'success': True,
            'file_id': file_id,
            'processing_time': elapsed,
            **result
        })

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<file_id>')
def download(file_id):
    for f in os.listdir(app.config['OUTPUT_FOLDER']):
        if f.startswith(file_id):
            return send_file(
                os.path.join(app.config['OUTPUT_FOLDER'], f),
                as_attachment=True,
                download_name=f
            )
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/preview/<file_id>')
def preview(file_id):
    for f in os.listdir(app.config['OUTPUT_FOLDER']):
        if f.startswith(file_id):
            return send_from_directory(app.config['OUTPUT_FOLDER'], f)
    return jsonify({'error': 'File not found'}), 404

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/css/<path:filename>')
def css_files(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), filename)

@app.route('/js/<path:filename>')
def js_files(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), filename)

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)

if __name__ == '__main__':
    print("=" * 50)
    print("  AI Image Resizer")
    print("  Open: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)