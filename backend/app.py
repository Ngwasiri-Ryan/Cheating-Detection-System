import cv2
import os
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load OpenCV's face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

@app.route("/")
def home():
    return "AI Cheating Detection API"

@app.route("/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "No video file uploaded"}), 400

    video_file = request.files["video"]
    video_path = os.path.join(app.config["UPLOAD_FOLDER"], video_file.filename)
    video_file.save(video_path)

    # Analyze video for cheating
    cheating_detected = analyze_video(video_path)

    return jsonify({"cheating_detected": cheating_detected, "video_path": video_path})


def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    cheating_detected = False
    frame_count = 0
    face_detected_frames = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            face_detected_frames += 1

        # If more than 80% of frames contain faces, assume no impersonation
        if frame_count > 20 and (face_detected_frames / frame_count) < 0.5:
            cheating_detected = True
            break

    cap.release()
    return cheating_detected


if __name__ == "__main__":
    app.run(debug=True)
