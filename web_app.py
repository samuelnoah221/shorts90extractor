from flask import Flask, render_template, request, send_from_directory, url_for
import os
import yt_dlp
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ColorClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

app = Flask(__name__)

# Strict 45MB device file safety block for free server preservation
app.config['MAX_CONTENT_LENGTH'] = 45 * 1024 * 1024 

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
    original_display_name = "Cloud Stream"

    # 🔗 BRANCH A: CLOUD SOCIAL LINK PROCESSING (INFINITE LENGTH SAFE ENGINE)
    if source_url and source_url.strip() != "":
        print(f"[CLOUD MATRIX] Initializing live time-sliced link feed: {source_url}")
        
        cloud_filename = "cloud_download.mp4"
        input_path = os.path.join(UPLOAD_FOLDER, cloud_filename)
        
        if os.path.exists(input_path):
            os.remove(input_path)
            
        ydl_opts = {
            'format': 'best[height<=720][ext=mp4]/best[ext=mp4]/best',
            'outtmpl': input_path,
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 15,
            # 🔥 ANY LENGTH BYPASS: Instructs cloud downloader to stream ONLY the first 30 seconds!
            'download_ranges': lambda info_dict, ydl: [{'start_time': 0, 'end_time': 30}],
            'force_generic_extractor': False,
            'extractor_args': {
                'youtube': {
                    'player_client': ['web_safari', 'ios'],
                    'skip': ['dash', 'hls']
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([source_url])
        except Exception as e:
            return f"""
            <body style="background-color: #0f172a; color: #f8fafc; font-family: sans-serif; padding: 40px; text-align: center;">
                <div style="background: #1e293b; max-width: 600px; margin: 0 auto; padding: 30px; border-radius: 12px; border: 1px solid #ef4444;">
                    <h2 style="color: #ef4444;">🔒 Ingestion Safeguard Active</h2>
                    <p style="color: #cbd5e1; text-align: left; font-size: 14px; line-height: 1.6;">
                        This platform URL has blocked external cloud server requests. 
                        <br><br>
                        <strong>💡 How to bypass this immediately:</strong> Upload a quick screen recording or short video clip (under 45MB) directly from your mobile phone or computer gallery. Device uploads bypass 100% of bot filters!
                    </p>
                    <a href="/dashboard" style="background: #0284c7; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; margin-top: 15px;">🔄 Return to Dashboard</a>
                </div>
            </body>
            """

    # 📁 BRANCH B: MOBILE / DESKTOP DIRECT FILE PAYLOAD
    elif video_file and video_file.filename != '':
        original_display_name = video_file.filename
        input_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
        video_file.save(input_path)
    else:
        return "Error: No file or streaming target link provided.", 400

    # 🎬 MOVIEPY RENDERING SUB-ENGINE
    try:
        clip = VideoFileClip(input_path)
        target_w = 720
        target_h = 1280
        
        duration_to_cut = min(clip.duration, 30)
        working_clip = clip.subclipped(0, duration_to_cut)
        
        if processing_mode == "smart_fit":
            scale_factor = min(target_w / working_clip.w, target_h / working_clip.h)
            scaled_clip = working_clip.resized(scale_factor)
            background = ColorClip(size=(target_w, target_h), color=(15, 23, 42)).with_duration(duration_to_cut)
            final_clip = CompositeVideoClip([background, scaled_clip.with_position("center")])
        else:
            crop_width = int(working_clip.w * 0.5625)
            x1 = int((working_clip.w - crop_width) / 2)
            final_clip = working_clip.cropped(x1=x1, y1=0, width=crop_width, height=working_clip.h).resized(newsize=(target_w, target_h))

        output_filename = f"short_{os.path.basename(input_path)}"
        if not output_filename.endswith('.mp4'):
            output_filename += '.mp4'
            
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Render the file
        final_clip.write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac", 
            fps=20, 
            logger=None,
            write_logfile=False
        )
        
        clip.close()
        final_clip.close()
        
        download_url = url_for('download_file', filename=output_filename)
        
        return f"""
        <body style="background-color: #0f172a; color: #f8fafc; font-family: sans-serif; padding: 40px; text-align: center;">
            <div style="background: #1e293b; max-width: 600px; margin: 0 auto; padding: 30px; border-radius: 12px; border: 1px solid #334155;">
                <h2 style="color: #38bdf8;">✨ Conversion Complete!</h2>
                <p style="font-size: 14px; color: #94a3b8;">Source Asset: <strong>{original_display_name}</strong></p>
                <p>Your short video clip has been successfully optimized into a 9:16 mobile frame.</p>
                
                <div style="background: #0f172a; border: 2px dashed #ec4899; padding: 15px; margin: 25px 0; border-radius: 6px;">
                    <p style="color: #64748b; margin: 0 0 5px 0; font-size: 11px; text-transform: uppercase;">Sponsored Network Ad Placement</p>
                    <a href="#" style="color: #38bdf8; font-weight: bold; text-decoration: none;">💎 Earn Passive Revenue Daily — Click to Integrate Ads on Your Own Traffic Pages Instantly!</a>
                </div>
                
                <a href="{download_url}" style="background: #0284c7; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; margin-bottom: 20px;">📥 Download Processed Short</a>
                <br>
                <a href="/dashboard" style="color: #cbd5e1; text-decoration: none; font-size: 14px;">← Process Another Video</a>
            </div>
        </body>
        """
    except Exception as e:
        print(f"[ENGINE EXCEPTION] {str(e)}")
        return f"<h3>Core Rendering Blocked</h3><p>Diagnostics: {str(e)}</p><a href='/dashboard'>Return to dashboard</a>", 500

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
