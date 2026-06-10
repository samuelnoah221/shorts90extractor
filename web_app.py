from flask import Flask, render_template, request, send_from_directory, url_for
import os
import yt_dlp
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
    
    # Secure numeric fallbacks for coordinates
    x = int(request.form.get('x', 0) or 0)
    y = int(request.form.get('y', 0) or 0)
    w = int(request.form.get('w', 100) or 100)
    h = int(request.form.get('h', 50) or 50)
    
    video_file = request.files.get('video_file')
    input_path = ""

    # 🔗 BRANCH A: PROCESS LIVE SOCIAL MEDIA URL
    if source_url and source_url.strip() != "":
        print(f"[CLOUD ENGINE] Initializing yt-dlp link download pipeline: {source_url}")
        
        # Unique filename template for this cloud download
        cloud_filename = "cloud_download.mp4"
        input_path = os.path.join(UPLOAD_FOLDER, cloud_filename)
        
        # Remove old cached cloud files if they exist to protect disk space
        if os.path.exists(input_path):
            os.remove(input_path)
            
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': input_path,
            'max_filesize': 30 * 1024 * 1024,
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 10,
            # 🔥 THE BYPASS MATRIX: Pretends to be Safari / Embedded Player Web View
            'extractor_args': {
                'youtube': {
                    'player_client': ['web_safari', 'ios'],
                    'skip': ['dash', 'hls']
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([source_url])
            print("[CLOUD ENGINE] Successfully ingested streaming content directly into server folder!")
        except Exception as e:
            return f"<h3>Ingestion Scraper Failed</h3><p>Could not download link stream. Reason: {str(e)}</p><a href='/dashboard'>Try another link</a>", 400

    # 📁 BRANCH B: PROCESS LOCAL FILE DRAG-AND-DROP
    elif video_file and video_file.filename != '':
        input_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
        video_file.save(input_path)
    else:
        return "Error: No URL link or dropped video file detected.", 400

    # 🎬 CORE VIDEO COMPRESSION & FORMATTING PIPELINE (MoviePy v2)
    try:
        clip = VideoFileClip(input_path)
        target_w = 720
        target_h = 1280
        
        # Cap clip length to 15 seconds max to guarantee super fast processing runs
        duration_to_cut = min(clip.duration, 15)
        working_clip = clip.subclipped(0, duration_to_cut)
        
        if processing_mode == "smart_fit":
            print("[ENGINE LOG] Executing smart-fit boundary padding protection layout...")
            scale_factor = min(target_w / working_clip.w, target_h / working_clip.h)
            scaled_clip = working_clip.resized(scale_factor)
            
            background = ColorClip(size=(target_w, target_h), color=(15, 23, 42)).with_duration(duration_to_cut)
            final_clip = CompositeVideoClip([background, scaled_clip.with_position("center")])
        else:
            print("[ENGINE LOG] Executing standard full-bleed centerpiece crop matrix...")
            crop_width = int(working_clip.w * 0.5625)
            x1 = int((working_clip.w - crop_width) / 2)
            final_clip = working_clip.cropped(x1=x1, y1=0, width=crop_width, height=working_clip.h)
            final_clip = final_clip.resized(newsize=(target_w, target_h))

        output_filename = f"short_out_{os.path.basename(input_path)}"
        if not output_filename.endswith('.mp4'):
            output_filename += '.mp4'
            
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Render the file
        final_clip.write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac",
            fps=24,
            logger=None
        )
        
        # Close handles instantly to free memory channels
        clip.close()
        final_clip.close()
        
        download_url = url_for('download_file', filename=output_filename)
        
        return f"""
        <body style="background-color: #0f172a; color: #f8fafc; font-family: sans-serif; padding: 40px; text-align: center;">
            <div style="background: #1e293b; max-width: 600px; margin: 0 auto; padding: 30px; border-radius: 12px; border: 1px solid #334155;">
                <h2 style="color: #38bdf8;">✨ Conversion Pipeline Complete!</h2>
                <p>Your social media clip has been downloaded, processed, and optimized without edge text cut-offs.</p>
                
                <div style="background: #0f172a; border: 2px dashed #475569; padding: 15px; margin: 25px 0; border-radius: 6px;">
                    <p style="color: #94a3b8; margin: 0 0 10px 0; font-size: 11px; text-transform: uppercase;">Sponsored Content Ad</p>
                    <a href="https://github.com/samuelnoah221" target="_blank" style="color: #38bdf8; font-weight: bold; text-decoration: none;">🚀 Maximize Your Reach! Get Viral Automated Templates Here!</a>
                </div>
                
                <a href="{download_url}" style="background: #0284c7; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; margin-bottom: 20px;">📥 Download Processed Short</a>
                <br>
                <a href="/dashboard" style="color: #cbd5e1; text-decoration: none; font-size: 14px;">← Process Another Video</a>
            </div>
        </body>
        """
    except Exception as e:
        print(f"[PROCESS CRASH] {str(e)}")
        return f"<h3>Core Rendering Blocked</h3><p>Error diagnostics: {str(e)}</p><a href='/dashboard'>Return to dashboard</a>", 500

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
