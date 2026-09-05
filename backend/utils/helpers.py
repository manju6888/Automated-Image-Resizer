import os

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_size_mb(filepath):
    return os.path.getsize(filepath) / (1024 * 1024)

def create_directories(directories):
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
