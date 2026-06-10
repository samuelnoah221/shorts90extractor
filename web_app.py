from flask import Flask, render_template, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'web_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/process', methods=['POST'])
def process_video():
    x = request.form.get('x')
    y = request.form.get('y')
    w = request.form.get('w')
    h = request.form.get('h')
    
    file = request.files['video_file']
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        print(f"[SYSTEM LOG] File saved safely at: {file_path}")
        print(f"[SYSTEM LOG] Watermark Target Matrix -> X:{x} Y:{y} W:{w} H:{h}")
        
    return f"<h3>Pipeline Active!</h3><p>Your video file '{file.filename}' was uploaded successfully onto your local server machine. Next up, we will stitch your processing code loops directly to this action response handler!</p><br><a href='/dashboard'>Return to Dashboard</a>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
