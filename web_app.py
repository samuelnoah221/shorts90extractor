import streamlit as st
import os
import cv2
import numpy as np
from moviepy import VideoFileClip

# 🔥 CRITICAL: Allow large video uploads up to 1000MB (1GB)
st.config.set_option("server.maxUploadSize", 1000)

# ==========================================
# PAGE CONFIGURATION & LAYOUT
# ==========================================
st.set_page_config(page_title="Shorts90 Extractor Portal", layout="centered")
st.title("🎬 Shorts90 Extractor Portal")
st.write("Upload your video to automatically extract 10 high-energy vertical shorts with watermark removal!")

# ==========================================
# USER INPUT INTERFACE
# ==========================================
st.sidebar.header("🛠️ Watermark Settings")
st.sidebar.write("Adjust where the watermark box sits on your video:")

x_coord = st.sidebar.number_input("X (Pixels from left)", min_value=0, value=40)
y_coord = st.sidebar.number_input("Y (Pixels from top)", min_value=0, value=40)
w_coord = st.sidebar.number_input("Width of Box", min_value=1, value=150)
h_coord = st.sidebar.number_input("Height of Box", min_value=1, value=60)

# Drag and Drop Box
uploaded_file = st.file_uploader("Drop your long video file here", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    upload_dir = "web_uploads"
    output_dir = "web_extracted_shorts"
    
    for folder in [upload_dir, output_dir]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            
    input_path = os.path.join(upload_dir, uploaded_file.name)
    
    # Save the uploaded file locally
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.success(f"✓ Video loaded: {uploaded_file.name}")
    st.video(input_path)

    # ==========================================
    # PROCESSING PIPELINE TRIGGER
    # ==========================================
    if st.button("✨ Extract Clean Shorts"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("Step 1: Reading video data and sound tracks...")
            clip = VideoFileClip(input_path)
            width, height = clip.size
            video_duration = clip.duration
            
            # Highlight Detection Math
            audio_frame_reader = clip.audio.to_soundarray(fps=22050)
            volume_profile = np.abs(audio_frame_reader[:, 0]) + np.abs(audio_frame_reader[:, 1])
            seconds_tracked = len(volume_profile) // 22050
            
            per_second_volume = []
            for i in range(seconds_tracked):
                chunk = volume_profile[i * 22050 : (i + 1) * 22050]
                per_second_volume.append(np.mean(chunk))
                
            loudest_seconds_sorted = np.argsort(per_second_volume)[::-1]
            
            short_duration = 45  
            target_shorts_count = 10
            chosen_start_times = []
            
            for second in loudest_seconds_sorted:
                if second + short_duration < video_duration and second > 5:
                    if all(abs(second - already_chosen) > (short_duration + 10) for already_chosen in chosen_start_times):
                        chosen_start_times.append(second)
                if len(chosen_start_times) >= target_shorts_count:
                    break
            chosen_start_times.sort()
            
            # Setup crop layout
            new_width = int(height * (9 / 16))
            x1 = (width - new_width) // 2
            x2 = x1 + new_width
            
            # Process loops
            for index, start_timestamp in enumerate(chosen_start_times):
                status_text.text(f"Processing Short {index + 1} of {len(chosen_start_times)}...")
                
                sub_clip = clip.subclipped(start_timestamp, start_timestamp + short_duration)
                cropped_clip = sub_clip.cropped(x1=x1, y1=0, x2=x2, y2=height)
                
                temp_raw = f"temp_web_{index}.mp4"
                cropped_clip.write_videofile(temp_raw, codec="libx264", audio_codec="aac", logger=None)
                
                # Inpainting logic loop
                cap = cv2.VideoCapture(temp_raw)
                fps = cap.get(cv2.CAP_PROP_FPS)
                fw, fh = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                temp_clean = f"temp_web_clean_{index}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(temp_clean, fourcc, fps, (fw, fh))
                
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret: break
                    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
                    mask[y_coord:y_coord+h_coord, x_coord:x_coord+w_coord] = 255
                    clean_frame = cv2.inpaint(frame, mask, 3, cv2.INPAINT_TELEA)
                    out.write(clean_frame)
                    
                cap.release()
                out.release()
                
                final_output_path = os.path.join(output_dir, f"clean_short_{index + 1}.mp4")
                clean_video_clip = VideoFileClip(temp_clean)
                final_clip = clean_video_clip.with_audio(sub_clip.audio)
                final_clip.write_videofile(final_output_path, codec="libx264", audio_codec="aac", logger=None)
                
                clean_video_clip.close()
                if os.path.exists(temp_raw): os.remove(temp_raw)
                if os.path.exists(temp_clean): os.remove(temp_clean)
                
                progress_bar.progress(int(((index + 1) / len(chosen_start_times)) * 100))
            
            status_text.text("🎉 All videos successfully rendered!")
            st.balloons()
            
            st.subheader("⬇️ Download Your Extracted Clips")
            for file in sorted(os.listdir(output_dir)):
                if file.endswith(".mp4"):
                    file_path = os.path.join(output_dir, file)
                    st.write(f"📁 {file}")
                    st.video(file_path)
                    
        except Exception as e:
            st.error(f"Execution failed: {e}")