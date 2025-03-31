import cv2
import dlib
import os
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import Tuple, Dict, List, Union

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cheating_detection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = "uploads"
MODEL_FOLDER = "models"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# File paths
FACE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
LANDMARK_PREDICTOR_PATH = os.path.join(MODEL_FOLDER, "shape_predictor_68_face_landmarks.dat")

# Verify model files exist
if not os.path.exists(FACE_CASCADE_PATH):
    error_msg = f"OpenCV face cascade file not found at {FACE_CASCADE_PATH}"
    logger.error(error_msg)
    raise FileNotFoundError(error_msg)

if not os.path.exists(LANDMARK_PREDICTOR_PATH):
    error_msg = (
        f"Facial landmark predictor not found at {LANDMARK_PREDICTOR_PATH}\n"
        "Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
    )
    logger.error(error_msg)
    raise FileNotFoundError(error_msg)
else:
    logger.info(f"Successfully found landmark predictor at {LANDMARK_PREDICTOR_PATH}")

# Initialize detectors
try:
    logger.info("Initializing face cascade classifier...")
    face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
    if face_cascade.empty():
        raise ValueError("Could not load face cascade classifier")
    logger.info("Face cascade initialized successfully")
except Exception as e:
    error_msg = f"Error loading face cascade: {str(e)}"
    logger.error(error_msg)
    raise RuntimeError(error_msg)

try:
    logger.info("Initializing dlib detectors...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(LANDMARK_PREDICTOR_PATH)
    logger.info("Dlib detectors initialized successfully")
except Exception as e:
    error_msg = f"Error initializing dlib detectors: {str(e)}"
    logger.error(error_msg)
    raise RuntimeError(error_msg)

def validate_and_convert_frame(frame: np.ndarray) -> Union[np.ndarray, None]:
    """Robust frame validation and conversion for dlib compatibility"""
    if frame is None:
        return None

    try:
        # Ensure 8-bit depth (critical for dlib)
        if frame.dtype != np.uint8:
            if np.issubdtype(frame.dtype, np.floating):
                frame = (frame * 255).clip(0, 255).astype(np.uint8)
            else:
                frame = frame.astype(np.uint8)

        # Handle all possible channel configurations
        if len(frame.shape) == 2:  # Grayscale
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        elif len(frame.shape) == 3:
            if frame.shape[2] == 1:  # Single channel
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            elif frame.shape[2] == 3:  # 3 channels
                pass  # Assume BGR (OpenCV default)
            elif frame.shape[2] == 4:  # RGBA
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
            else:
                return None  # Unsupported channel count

        # Final conversion to RGB for dlib
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return rgb_frame

    except Exception as e:
        logger.error(f"Frame conversion error: {str(e)}")
        return None

@app.route("/")
def home() -> str:
    """Root endpoint that returns a simple welcome message"""
    return "AI Cheating Detection API"

@app.route("/upload", methods=["POST"])
def upload_video() -> Tuple[Dict, int]:
    """
    Handle video file upload and process it for cheating detection
    Returns:
        JSON response with cheating detection results
    """
    if "video" not in request.files:
        return jsonify({"error": "No video file uploaded"}), 400

    video_file = request.files["video"]
    if video_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    video_path = os.path.join(app.config["UPLOAD_FOLDER"], video_file.filename)
    try:
        video_file.save(video_path)
        logger.info(f"Video saved successfully at {video_path}")
        
        # Log video properties
        cap = cv2.VideoCapture(video_path)
        logger.info(f"Video properties - Codec: {int(cap.get(cv2.CAP_PROP_FOURCC))}, "
                   f"Width: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}, "
                   f"Height: {int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}, "
                   f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
        cap.release()
        
    except Exception as e:
        logger.error(f"Error saving video: {str(e)}")
        return jsonify({"error": f"Error saving video: {str(e)}"}), 500

    cheating_detected, details = analyze_video(video_path)
    return jsonify({
        "cheating_detected": cheating_detected,
        "details": details,
        "video_path": video_path
    })

def analyze_video(video_path: str) -> Tuple[bool, Dict]:
    """
    Analyze video for cheating behavior using face detection and eye tracking
    Args:
        video_path: Path to the video file to analyze
    Returns:
        Tuple of (cheating_detected, details) where details contains detection statistics
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error("Could not open video file")
        return False, {"error": "Could not open video file"}

    frame_count = 0
    face_detected_frames = 0
    eye_lookaway_frames = 0
    multiple_faces_detected = False
    cheating_detected = False
    reasons = []

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            logger.debug(f"Processing frame {frame_count}")

            # Validate and convert frame
            frame = validate_and_convert_frame(frame)
            if frame is None:
                logger.warning(f"Skipping invalid frame {frame_count}")
                continue

            try:
                # Convert to RGB for dlib operations
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to grayscale for OpenCV face detection
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # OpenCV face detection (grayscale)
                faces = face_cascade.detectMultiScale(
                    gray_frame, 
                    scaleFactor=1.1, 
                    minNeighbors=5, 
                    minSize=(30, 30),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                
                # Dlib face detection (RGB)
                faces_dlib = detector(rgb_frame, 1)

                if len(faces) > 1 or len(faces_dlib) > 1:
                    multiple_faces_detected = True
                    reasons.append("Multiple faces detected")

                for face in faces_dlib:
                    face_detected_frames += 1
                    
                    # Facial landmarks (RGB)
                    shape = predictor(rgb_frame, face)
                    
                    # Eye tracking logic
                    left_eye = shape.part(36)
                    right_eye = shape.part(45)
                    nose_left = shape.part(31)
                    nose_right = shape.part(35)
                    
                    eye_distance = abs(left_eye.x - right_eye.x)
                    nose_width = abs(nose_left.x - nose_right.x)
                    
                    if eye_distance < 0.6 * nose_width:
                        eye_lookaway_frames += 1
                        reasons.append("Eyes not centered")

            except Exception as e:
                logger.error(f"Error processing frame {frame_count}: {str(e)}")
                continue

            # Early termination conditions
            if multiple_faces_detected:
                cheating_detected = True
                reasons = ["Multiple faces detected"]  # Override previous reasons
                break

            if frame_count >= 30:  # Analyze first 30 frames
                face_ratio = face_detected_frames / frame_count
                lookaway_ratio = eye_lookaway_frames / max(1, face_detected_frames)

                if face_ratio < 0.5:
                    cheating_detected = True
                    reasons.append("Face not detected consistently")
                    break

                if lookaway_ratio > 0.4:
                    cheating_detected = True
                    reasons.append("Looking away too frequently")
                    break

    finally:
        cap.release()
    
    if not reasons:
        reasons.append("No cheating detected")

    return cheating_detected, {
        "reasons": list(set(reasons)),
        "statistics": {
            "total_frames": frame_count,
            "face_detection_rate": face_detected_frames/frame_count if frame_count else 0,
            "lookaway_ratio": eye_lookaway_frames/max(1, face_detected_frames)
        }
    }

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)