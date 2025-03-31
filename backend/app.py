import cv2
import dlib
import os
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import Tuple, Dict, List, Optional
from collections import defaultdict
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
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

# Model paths
FACE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
LANDMARK_PREDICTOR_PATH = os.path.join(MODEL_FOLDER, "shape_predictor_68_face_landmarks.dat")

# Initialize detectors
try:
    face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(LANDMARK_PREDICTOR_PATH)
except Exception as e:
    logger.error(f"Initialization error: {str(e)}")
    raise

def validate_and_convert_frame(frame: np.ndarray) -> Optional[np.ndarray]:
    """Ensure frame is in correct format for analysis"""
    if frame is None:
        return None
        
    try:
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)
            
        if len(frame.shape) == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        elif len(frame.shape) == 3:
            if frame.shape[2] == 1:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            elif frame.shape[2] == 3:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            elif frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
                
        return frame
    except Exception as e:
        logger.error(f"Frame conversion error: {str(e)}")
        return None

def analyze_single_frame(frame: np.ndarray) -> Optional[Dict]:
    """Analyze a single keyframe"""
    frame = validate_and_convert_frame(frame)
    if frame is None:
        return None
        
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        results = {
            'face_detections': 0,
            'lookaway_count': 0,
            'multiple_faces': False
        }
        
        # OpenCV face detection
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        
        # Dlib face detection
        faces_dlib = detector(frame, 1)
        
        if len(faces) > 1 or len(faces_dlib) > 1:
            results['multiple_faces'] = True
            
        for face in faces_dlib:
            results['face_detections'] += 1
            shape = predictor(frame, face)
            
            # Eye tracking
            left_eye = shape.part(36)
            right_eye = shape.part(45)
            nose_left = shape.part(31)
            nose_right = shape.part(35)
            
            if abs(left_eye.x - right_eye.x) < 0.6 * abs(nose_left.x - nose_right.x):
                results['lookaway_count'] += 1
                
        return results
        
    except Exception as e:
        logger.error(f"Frame analysis error: {str(e)}")
        return None


# [Previous imports and configuration remain the same until analyze_video_keyframes]

def analyze_video_keyframes(video_path: str, keyframe_interval: int = 30) -> Tuple[bool, Dict]:
    """Main analysis using keyframe extraction with detailed logging"""
    cap = cv2.VideoCapture(video_path)
    results = defaultdict(int)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    processed_frames = 0
    
    # Log video properties
    logger.info(f"Starting analysis of {video_path}")
    logger.info(f"Total frames: {total_frames}, Keyframe interval: {keyframe_interval}")
    logger.info(f"Video properties - {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))} @ {cap.get(cv2.CAP_PROP_FPS):.2f}fps")
    
    frame_counter = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_counter += 1
        
        # Only process keyframes (every N frames)
        if frame_counter % keyframe_interval != 0:
            continue
            
        logger.debug(f"Processing frame {frame_counter}/{total_frames}")
        
        frame_result = analyze_single_frame(frame)
        if frame_result:
            for k, v in frame_result.items():
                results[k] += v
            processed_frames += 1
            
            # Log frame-specific results
            if frame_result['face_detections'] > 0:
                logger.debug(f"Frame {frame_counter}: Detected {frame_result['face_detections']} face(s)")
                if frame_result['lookaway_count'] > 0:
                    logger.debug(f"Frame {frame_counter}: {frame_result['lookaway_count']} lookaway(s) detected")
            else:
                logger.debug(f"Frame {frame_counter}: No faces detected")
            
        # Early termination if cheating detected
        if results.get('multiple_faces', False):
            logger.warning("Early termination - Multiple faces detected")
            break
            
    cap.release()
    
    results['total_frames'] = total_frames
    results['processed_frames'] = processed_frames
    
    # Log summary before returning
    logger.info(f"Analysis completed. Processed {processed_frames}/{total_frames} frames ({processed_frames/total_frames*100:.1f}%)")
    logger.info(f"Total face detections: {results['face_detections']}")
    logger.info(f"Total lookaways detected: {results['lookaway_count']}")
    if results.get('multiple_faces', False):
        logger.warning("Cheating detected: Multiple faces in frame")
    
    return compile_results(results)

# [Rest of the code remains the same]

def compile_results(raw_results: Dict) -> Tuple[bool, Dict]:
    """Convert raw counts to final results"""
    cheating_detected = False
    reasons = []
    
    if raw_results.get('multiple_faces', False):
        cheating_detected = True
        reasons.append("Multiple faces detected")
    
    if raw_results['processed_frames'] > 0:
        face_ratio = raw_results['face_detections'] / raw_results['processed_frames']
        if face_ratio < 0.5:
            cheating_detected = True
            reasons.append("Low face detection rate")
            
        if raw_results['face_detections'] > 0:
            lookaway_ratio = raw_results['lookaway_count'] / raw_results['face_detections']
            if lookaway_ratio > 0.4:
                cheating_detected = True
                reasons.append("Excessive lookaways detected")
    
    return cheating_detected, {
        'reasons': reasons if reasons else ["No cheating detected"],
        'statistics': {
            'total_frames': raw_results['total_frames'],
            'processed_frames': raw_results['processed_frames'],
            'processing_ratio': f"{(raw_results['processed_frames']/raw_results['total_frames'])*100:.1f}%",
            'face_detection_rate': f"{(raw_results['face_detections']/raw_results['processed_frames'])*100:.1f}%" if raw_results['processed_frames'] > 0 else "0%"
        }
    }

def is_video_valid(video_path: str) -> bool:
    """Validate video file can be opened and has frames"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return False
    ret, _ = cap.read()
    cap.release()
    return ret

def analyze_video_keyframes(video_path: str, keyframe_interval: int = 30) -> Tuple[bool, Dict]:
    """Main analysis using keyframe extraction"""
    cap = cv2.VideoCapture(video_path)
    results = defaultdict(int)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    processed_frames = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Only process keyframes (every N frames)
        if cap.get(cv2.CAP_PROP_POS_FRAMES) % keyframe_interval != 0:
            continue
            
        frame_result = analyze_single_frame(frame)
        if frame_result:
            for k, v in frame_result.items():
                results[k] += v
            processed_frames += 1
            
        # Early termination if cheating detected
        if results.get('multiple_faces', False):
            break
            
    cap.release()
    
    results['total_frames'] = total_frames
    results['processed_frames'] = processed_frames
    return compile_results(results)

@app.route("/")
def home() -> str:
    return "AI Cheating Detection API (Keyframe Method)"

@app.route("/upload", methods=["POST"])
def upload_video() -> Tuple[Dict, int]:
    if "video" not in request.files:
        return jsonify({"error": "No video file uploaded"}), 400

    video_file = request.files["video"]
    if video_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        video_path = os.path.join(app.config["UPLOAD_FOLDER"], video_file.filename)
        video_file.save(video_path)
        logger.info(f"Video saved to {video_path}")
        
        if not is_video_valid(video_path):
            return jsonify({"error": "Invalid video file"}), 400
            
        cheating_detected, details = analyze_video_keyframes(video_path)
        return jsonify({
            "cheating_detected": cheating_detected,
            "details": details,
            "video_path": video_path
        })
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return jsonify({"error": f"Error processing video: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)