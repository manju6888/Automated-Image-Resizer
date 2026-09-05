<<<<<<< HEAD
\# Automated Image Resizer Service



Deep Learning powered image resizer using Flask + PyTorch + OpenCV.



\## Features

\- Smart AI Resize

\- Super Resolution (upscale 2x, 3x, 4x)

\- Exact size \& percentage scaling

\- PNG / JPG / WebP output

\- Before/After preview

\- Download resized image



\## How to Run



```bash

\# Activate virtual environment

venv\\Scripts\\activate



\# Start server

python backend\\app.py

=======
# 🖼️ Automated Image Resizer Service

A **Deep Learning powered** web application and API service for intelligent image resizing, upscaling, and super-resolution. Built with **PyTorch**, **OpenCV**, and **Flask**.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.1.2-ee4c2c)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9-5C3EE8)

---

## ✨ Features

- 🧠 **AI-Powered Super Resolution**: Upscale images up to 4x using ESPCN & SRCNN Neural Networks without quality loss.
- 🎨 **Smart AI Resizing**: Intelligent content-aware resizing that preserves image sharpness.
- 📐 **Multiple Modes**:
  - **Smart AI**: Automatic high-quality scaling.
  - **Super Resolution**: Deep Learning upscaling (2x, 3x, 4x).
  - **Exact Dimensions**: Custom width and height pixel input.
  - **Percentage Scaling**: Scale images by ratio (0.5x, 1x, 2x, etc.).
- 🔄 **Format Conversion**: Output to PNG, JPG, or WebP.
- ⚡ **Real-Time Preview**: Side-by-side comparison of original vs resized images.
- 🛠️ **REST API**: Fully programmatic endpoint for automated image uploads & downloads.

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Flask-CORS, PyTorch, Torchvision, OpenCV, NumPy
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), FontAwesome
- **Environment**: Virtual Environment (`venv`)

---

## 📁 Project Structure
automated-image-resizer/
├── backend/
│ ├── app.py # Main Flask Server & API routes
│ ├── requirements.txt # Python dependencies
│ ├── models/
│ │ ├── init.py
│ │ └── super_resolution.py # PyTorch Super-Resolution & CNN Models
│ ├── services/
│ │ ├── init.py
│ │ └── image_service.py # Image processing pipeline
│ ├── utils/
│ │ ├── init.py
│ │ └── helpers.py # Utility helper functions
│ ├── uploads/ # Temporary upload directory
│ └── outputs/ # Saved processed images
├── frontend/
│ ├── index.html # Main UI Page
│ ├── css/
│ │ └── style.css # UI Styling
│ └── js/
│ └── app.js # Frontend AJAX & Logic
├── start.bat # Windows Auto-Start script
├── README.md # Documentation
└── .gitignore # Ignored files

text


---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/manju6888/automated-image-resizer.git
cd automated-image-resizer
2. Activate Virtual Environment
Bash

# Windows Command Prompt
venv\Scripts\activate
3. Install Dependencies
Bash

pip install -r backend/requirements.txt
4. Run the Server
Bash

python backend/app.py
Or simply double-click start.bat on Windows.

5. Access the App
Open your browser and navigate to:

text

http://localhost:5000
📡 API Endpoints
Method	Endpoint	Description
GET	/api/health	Server & Neural Network Status
POST	/api/upload	Upload & Process an Image
GET	/api/preview/<file_id>	Preview Processed Image
GET	/api/download/<file_id>	Download Processed Image
Example Upload API Request (cURL):
Bash

curl -X POST http://localhost:5000/api/upload \
  -F "image=@my_photo.jpg" \
  -F "resize_mode=super_resolution" \
  -F "scale_factor=2" \
  -F "output_format=png"
👤 Author
GitHub: @manju6888
📜 License
This project is open-source under the MIT License.

text


---

### Step 3: Save and Push to GitHub

In Notepad: press **Ctrl + S**, then close Notepad.

Now run these 3 commands in Command Prompt to push the README to your repository:

```cmd
git add README.md
git commit -m "Add documentation README.md"
git push origin main
>>>>>>> fa8f0a6b3d6ffd00823a0859d3643685a1a88409
