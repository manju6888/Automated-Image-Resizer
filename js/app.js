// Automatically detect backend URL
const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:5000/api'
    : 'http://localhost:5000/api'; 

const fileInput = document.getElementById('fileInput');
const dropzone = document.getElementById('dropzone');
const preview = document.getElementById('preview');
const imgInfo = document.getElementById('imgInfo');
const btn = document.getElementById('btn');
const resultCard = document.getElementById('resultCard');

let selectedFile = null;

if (dropzone) {
    dropzone.addEventListener('click', () => fileInput.click());
    dropzone.addEventListener('dragover', e => { e.preventDefault(); dropzone.style.borderColor = '#6366f1'; });
    dropzone.addEventListener('dragleave', () => { dropzone.style.borderColor = '#475569'; });
    dropzone.addEventListener('drop', e => {
        e.preventDefault();
        dropzone.style.borderColor = '#475569';
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });
}

if (fileInput) {
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) handleFile(fileInput.files[0]);
    });
}

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }
    selectedFile = file;
    const reader = new FileReader();
    reader.onload = e => {
        preview.src = e.target.result;
        preview.style.display = 'block';
        const img = new Image();
        img.onload = () => {
            imgInfo.textContent = `${img.width} × ${img.height} px | ${(file.size / 1024).toFixed(1)} KB`;
        };
        img.src = e.target.result;
        btn.disabled = false;
    };
    reader.readAsDataURL(file);
}

if (btn) {
    btn.addEventListener('click', async () => {
        if (!selectedFile) return;

        btn.disabled = true;
        btn.textContent = 'Processing...';

        const fd = new FormData();
        fd.append('image', selectedFile);
        fd.append('resize_mode', document.getElementById('mode').value);
        fd.append('scale_factor', document.getElementById('scale').value);
        fd.append('output_format', document.getElementById('format').value);
        fd.append('maintain_aspect', 'true');
        fd.append('quality', '95');

        const w = document.getElementById('width').value;
        const h = document.getElementById('height').value;
        if (w) fd.append('width', w);
        if (h) fd.append('height', h);

        try {
            const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: fd });
            
            if (!res.ok) {
                throw new Error(`Server returned HTTP ${res.status}. Make sure backend server is running!`);
            }

            const data = await res.json();

            if (!data.success) {
                alert('Error: ' + (data.error || 'Unknown error'));
                return;
            }

            resultCard.style.display = 'block';
            document.getElementById('origResult').src = preview.src;
            document.getElementById('newResult').src = data.preview_url.startsWith('http') 
                ? data.preview_url 
                : `${API_BASE.replace('/api', '')}${data.preview_url}?t=${Date.now()}`;

            document.getElementById('origStats').textContent =
                `${data.original_dimensions.width} × ${data.original_dimensions.height} | ${data.original_size_mb} MB`;

            document.getElementById('newStats').textContent =
                `${data.result_dimensions.width} × ${data.result_dimensions.height} | ${data.output_size_mb} MB`;

            document.getElementById('procInfo').textContent =
                `Scale: ${data.scale_applied}x | Mode: ${data.resize_mode} | Time: ${data.processing_time}s`;

            const downloadLink = document.getElementById('downloadLink');
            downloadLink.href = data.download_url.startsWith('http') 
                ? data.download_url 
                : `${API_BASE.replace('/api', '')}${data.download_url}`;

            resultCard.scrollIntoView({ behavior: 'smooth' });

        } catch (err) {
            alert('Backend Error: Python server is not reachable!\n\nPlease run "python backend/app.py" or "start.bat" on your PC, then try again at http://localhost:5000');
            console.error(err);
        }

        btn.disabled = false;
        btn.textContent = 'Resize Image';
    });
}