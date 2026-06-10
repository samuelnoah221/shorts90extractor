from flask import Flask, render_template, request, send_from_directory, url_for
import os
from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip

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
    # 1. Capture user customization payloads from dashboard form
    source_url = request.form.get('source_url')
    processing_mode = request.form.get('processing_mode') # 'smart_fit' or 'direct_crop'
    
    # Coordinates for watermark erasure tracking
    x = request.form.get('x', 0)
    y = request.form.get('y', 0)
    w = request.form.get('w', 100)
    h = request.form.get('h', 50)
    
    video_file = request.files.get('video_file')
    input_path = ""

    # 2. Check if user provided a raw file or a social media cloud link
    if source_url:
        # Placeholder for Cloud Scraper Stream Logic (yt_dlp engine integration)
        print(f"[CLOUD INGESTION] Initializing cloud stream fetcher for: {source_url}")
        return "<h3>Cloud Link Engine Booting</h3><p>Direct social media links require yt-dlp setup on the server hosting platform. Let's finish the media renderer engine first!</p><br><a href='/dashboard'>Back</a>"
    
    elif video_file and video_file.filename != '':
        input_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
        video_file.save(input_path)
    else:
        return "Error: No video payload detected. Please provide a file or a valid URL link.", 400

    try:
        # 3. Core Media Engine Execution
        clip = VideoFileClip(input_path)
        
        # Target Dimensions for Shorts / Reels standard (9:16 aspect ratio)
        target_w = 720
        target_h = 1280
        
        if processing_mode == "smart_fit":
            print("[ENGINE LOG] Running Smart-Fit compression pipeline to protect video borders...")
            # Calculate aspect ratios to scale down video without cropping native words/elements
            scale_factor = min(target_w / clip.w, target_h / clip.h)
            scaled_clip = clip.resize(scale_factor)
            
            # Generate a professional dark background canvas to anchor the scaled clip
            background = ColorClip(size=(target_w, target_h), color=(15, 23, 42)).set_duration(clip.duration)
            
            # Position the full source frame centered perfectly inside the 9:16 layout
            final_clip = CompositeVideoClip([background, scaled_clip.set_position("center")])
        else:
            print("[ENGINE LOG] Running standard centerpiece extraction crop matrix...")
            # Fallback to center-crop if user explicitly demands a full-bleed vertical display
            final_clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=clip.w*0.5625, height=clip.h)
            final_clip = final_clip.resize(newsize=(target_w, target_h))

        # Restrict rendering processes to a maximum duration to conserve free-tier cloud resources
        output_filename = f"short_{video_file.filename}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Render the final composite layout
        final_clip.subclip(0, min(clip.duration, 30)).write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac",
            fps=24,
            logger=None
        )
        
        # Clear hardware cache leaks
        clip.close()
        final_clip.close()
        
        download_url = url_for('download_file', filename=output_filename)
        
        # 4. Success payload embedded with strategic monetized components
        return f"""
        <body style="background-color: #0f172a; color: #f8fafc; font-family: sans-serif; padding: 40px; text-align: center;">
            <div style="background: #1e293b; max-width: 600px; margin: 0 auto; padding: 30px; border-radius: 12px; border: 1px solid #334155;">
                <h2 style="color: #38bdf8;">✨ Extraction Pipeline Complete!</h2>
                <p>Your vertical video short has been processed perfectly with boundary compression protectors active.</p>
                
                <div style="background: #0f172a; border: 2px dashed #475569; padding: 15px; margin: 25px 0; border-radius: 6px;">
                    <p style="color: #94a3b8; margin: 0 0 10px 0; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">Sponsored Advertisement</p>
                    <a href="https://github.com/samuelnoah221" target="_blank" style="color: #38bdf8; font-weight: bold; text-decoration: none;">🚀 Boost Your Engineering Workflow - Check Out Our Premium Tools!</a>
                </div>
                
                <a href="{download_url}" style="background: #0284c7; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; margin-bottom: 20px;">📥 Download Processed Short File</a>
                <br>
                <a href="/dashboard" style="color: #cbd5e1; text-decoration: none; font-size: 14px;">← Process Another Video</a>
            </div>
        </body>
        """
    except Exception as e:
        print(f"[SYSTEM CRITICAL CRASH] {str(e)}")
        return f"<h3>Processing Pipeline Halted</h3><p>Internal diagnostics error: {str(e)}</p><a href='/dashboard'>Return to try again</a>", 500

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
