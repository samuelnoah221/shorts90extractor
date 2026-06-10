from flask import Flask, render_template, request, send_from_directory, url_for
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

app = Flask(__name__)

UPLOAD_FOLDER = 'web_uploads'
OUTPUT_FOLDER = 'processed_outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/process', methods=['POST'])
def process_video():
    source_url = request.form.get('source_url')
    processing_mode = request.form.get('processing_mode')
    
    # Secure numeric fallback options for cropping boundaries
    x = int(request.form.get('x', 0) or 0)
    y = int(request.form.get('y', 0) or 0)
    w = int(request.form.get('w', 100) or 100)
    h = int(request.form.get('h', 50) or 50)
    
    video_file = request.files.get('video_file')
    input_path = ""

    # BRANCH A: Process Cloud Link Ingestion
    if source_url and source_url.strip() != "":
        print(f"[CLOUD INGESTION] Initializing fetch pipeline for URL: {source_url}")
        # Placeholder for our upcoming backend link scraper tool (yt_dlp core loop)
        return f"""
        <body style="background-color: #0f172a; color: #f8fafc; font-family: sans-serif; text-align: center; padding: 50px;">
            <div style="background: #1e293b; max-width: 500px; margin: 0 auto; padding: 30px; border-radius: 8px; border: 1px solid #334155;">
                <h3 style="color: #f43f5e;">🔗 Cloud Scraping Core Route Hit</h3>
                <p>Ingestion Target: <strong>{source_url}</strong></p>
                <p>We verified the link handler loop! Next step is connecting the yt-dlp scraping binary package so your server can download directly from the cloud.</p>
                <br><a href="/dashboard" style="color: #38bdf8; text-decoration: none;">Return to Workspace</a>
            </div>
        </body>
        """
    
    # BRANCH B: Process Drag-and-Drop or Local File Choice
    elif video_file and video_file.filename != '':
        input_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
        video_file.save(input_path)
    else:
        return "Error Error: No streaming link or file payload detected. Drop a file or enter a valid URL.", 400

    try:
        # Load the newly uploaded source media
        clip = VideoFileClip(input_path)
        
        # Target layout settings for matching standard Shorts formats
        target_w = 720
        target_h = 1280
        
        if processing_mode == "smart_fit":
            print("[ENGINE LOG] Running Smart-Fit compression padding routine...")
            # Calculate ratio scale factor to preserve text/elements on outer borders
            scale_factor = min(target_w / clip.w, target_h / clip.h)
            scaled_clip = clip.resized(scale_factor)
            
            # Form clean slate canvas block backdrop
            background = ColorClip(size=(target_w, target_h), color=(15, 23, 42)).with_duration(clip.duration)
            final_clip = CompositeVideoClip([background, scaled_clip.with_position("center")])
        else:
            print("[ENGINE LOG] Running centerpiece full-bleed extraction crop matrix...")
            # Using MoviePy v2.X outplace '.cropped()' syntax structure
            crop_width = int(clip.w * 0.5625)
            x1 = int((clip.w - crop_width) / 2)
            final_clip = clip.cropped(x1=x1, y1=0, width=crop_width, height=clip.h)
            final_clip = final_clip.resized(newsize=(target_w, target_h))

        output_filename = f"short_{video_file.filename}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Keep process lengths limited to protect free tier instance CPU runtimes
        final_clip.subclipped(0, min(clip.duration, 20)).write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac",
            fps=24,
            logger=None
        )
        
        clip.close()
        final_clip.close()
        
        download_url = url_for('download_file', filename=output_filename)
        
        return f"""
        <body style="background-color: #0f172a; color: #f8fafc; font-family: sans-serif; padding: 40px; text-align: center;">
            <div style="background: #1e293b; max-width: 600px; margin: 0 auto; padding: 30px; border-radius: 12px; border: 1px solid #334155;">
                <h2 style="color: #38bdf8;">✨ Extraction Pipeline Complete!</h2>
                <p>Your short file is processed and boundary-safeguarded.</p>
                
                <div style="background: #0f172a; border: 2px dashed #475569; padding: 15px; margin: 25px 0; border-radius: 6px;">
                    <p style="color: #94a3b8; margin: 0 0 10px 0; font-size: 11px; text-transform: uppercase;">Sponsored Placement</p>
                    <a href="https://github.com/samuelnoah221" target="_blank" style="color: #38bdf8; font-weight: bold; text-decoration: none;">🚀 Traffic Accelerator Tools — Boost Your Scaling Speeds!</a>
                </div>
                
                <a href="{download_url}" style="background: #0284c7; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; margin-bottom: 20px;">📥 Download Processed Short File</a>
                <br>
                <a href="/dashboard" style="color: #cbd5e1; text-decoration: none; font-size: 14px;">← Process Another Video</a>
            </div>
        </body>
        """
    except Exception as e:
        return f"<h3>Processing Pipeline Halted</h3><p>Internal diagnostics error: {str(e)}</p><a href='/dashboard'>Return to try again</a>", 500

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
