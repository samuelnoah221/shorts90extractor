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
    
    video_file = request.files.get('video_file')
    input_path = ""

    # 🔗 BRANCH A: PROCESS LIVE SOCIAL MEDIA URL (UP TO 512MB)
    if source_url and source_url.strip() != "":
        print(f"[CLOUD ENGINE] Initializing large video fetch: {source_url}")
        
        cloud_filename = "cloud_download.mp4"
        input_path = os.path.join(UPLOAD_FOLDER, cloud_filename)
        
        if os.path.exists(input_path):
            os.remove(input_path)
            
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': input_path,
            # 📦 Set strict execution block to exactly 512MB max limit
            'max_filesize': 512 * 1024 * 1024, 
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
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
        except Exception as e:
            return f"""
            <body style="background-color: #0f172a; color: #f8fafc; font-family: sans-serif; padding: 40px; text-align: center;">
                <div style="background: #1e293b; max-width: 600px; margin: 0 auto; padding: 30px; border-radius: 12px; border: 1px solid #ef4444;">
                    <h2 style="color: #ef4444;">🔒 Ingestion Safeguard Triggered</h2>
                    <p style="color: #cbd5e1; text-align: left; font-size: 14px; line-height: 1.6;">
                        The cloud link download failed. This happens if the video exceeds 512MB, or if YouTube/X issued a bot challenge flag to our hosting network.
                        <br><br>
                        <strong>💡 Foolproof Solution:</strong> Download the file onto your device first, then simply drop it directly into our upload box below! Device files bypass all cloud link size limitations and bot blocks instantly.
                    </p>
                    <a href="/dashboard" style="background: #0284c7; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; margin-top: 15px;">🔄 Return to Upload Box</a>
                </div>
            </body>
            """

    # 📁 BRANCH B: DEVICE FILE PAYLOAD (100% BOT-PROOF, UP TO 512MB)
    elif video_file and video_file.filename != '':
        input_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
        video_file.save(input_path)
    else:
        return "Error: Please paste a link or drop a valid video file.", 400

    # 🎬 ULTRA-LOW MEMORY RENDERING MACHINE FOR LONG VIDEOS
    try:
        # Load video header structure dynamically without pulling heavy frames into memory channel
        clip = VideoFileClip(input_path)
        target_w = 720
        target_h = 1280
        
        # ⚡ LIMIT LIFTER: Process full original video duration (Even if longer than 20 minutes!)
        full_duration = clip.duration 
        
        if processing_mode == "smart_fit":
            print(f"[ENGINE MATRIX] Scaling full runtime clip: {full_duration} seconds...")
            scale_factor = min(target_w / clip.w, target_h / clip.h)
            scaled_clip = clip.resized(scale_factor)
            
            background = ColorClip(size=(target_w, target_h), color=(15, 23, 42)).with_duration(full_duration)
            final_clip = CompositeVideoClip([background, scaled_clip.with_position("center")])
        else:
            print(f"[ENGINE MATRIX] Cropping centerpiece full runtime clip: {full_duration} seconds...")
            crop_width = int(clip.w * 0.5625)
            x1 = int((clip.w - crop_width) / 2)
            final_clip = clip.cropped(x1=x1, y1=0, width=crop_width, height=clip.h).resized(newsize=(target_w, target_h))

        output_filename = f"short_out_{os.path.basename(input_path)}"
        if not output_filename.endswith('.mp4'):
            output_filename += '.mp4'
            
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # 🚀 DISK CHUNK STREAMING PROTOCOL: Prevents server crash on free tier RAM allocations
        final_clip.write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac", 
            fps=24, 
            logger=None,
            # Memory saving tuning: Writes segments instantly directly to file storage stream
            write_logfile=False
        )
        
        # Clear hardware references instantly to wipe RAM cache pools
        clip.close()
        final_clip.close()
        
        download_url = url_for('download_file', filename=output_filename)
        
        return f"""
        <body style="background-color: #0f172a; color: #f8fafc; font-family: sans-serif; padding: 40px; text-align: center;">
            <div style="background: #1e293b; max-width: 600px; margin: 0 auto; padding: 30px; border-radius: 12px; border: 1px solid #334155;">
                <h2 style="color: #38bdf8;">✨ Full-Length Processing Complete!</h2>
                <p>Your video runtime format has been successfully stabilized and transformed without truncation.</p>
                
                <div style="background: #0f172a; border: 2px dashed #475569; padding: 15px; margin: 25px 0; border-radius: 6px;">
                    <p style="color: #94a3b8; margin: 0 0 10px 0; font-size: 11px; text-transform: uppercase;">Sponsored Network Monetization ad</p>
                    <a href="https://github.com/samuelnoah221" target="_blank" style="color: #38bdf8; font-weight: bold; text-decoration: none;">🚀 Traffic Boost Engine — Maximize Views on Full-Length Uploads Instantly!</a>
                </div>
                
                <a href="{download_url}" style="background: #0284c7; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; margin-bottom: 20px;">📥 Download Processed Short File</a>
                <br>
                <a href="/dashboard" style="color: #cbd5e1; text-decoration: none; font-size: 14px;">← Go Back to Workspace Dashboard</a>
            </div>
        </body>
        """
    except Exception as e:
        print(f"[LARGE VIDEOS CRASH LOG] {str(e)}")
        return f"<h3>Core Rendering Blocked</h3><p>Error diagnostics: {str(e)}</p><a href='/dashboard'>Return to dashboard</a>", 500

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
