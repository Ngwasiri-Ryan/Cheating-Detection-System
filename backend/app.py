
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
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'cheating_detection_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
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
    logger.info("Models loaded successfully")
except Exception as e:
    logger.error(f"Initialization error: {str(e)}")
    raise

def validate_and_convert_frame(frame: np.ndarray) -> Optional[np.ndarray]:
    """Ensure frame is in correct format for analysis"""
    if frame is None:
        logger.warning("Received None frame")
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



def analyze_single_frame(frame: np.ndarray, frame_number: int) -> Optional[Dict]:
    """Analyze a single keyframe with detailed logging"""
    frame = validate_and_convert_frame(frame)
    if frame is None:
        logger.warning(f"Frame {frame_number} - Invalid frame")
        return None
        
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        results = {
            'face_detections': 0,
            'lookaway_count': 0,
            'multiple_faces': False,
            'frame_number': frame_number
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
        
        logger.info(f"Frame {frame_number} - OpenCV faces: {len(faces)}, Dlib faces: {len(faces_dlib)}")
        
        if len(faces) > 1 or len(faces_dlib) > 1:
            results['multiple_faces'] = True
            logger.warning(f"Frame {frame_number} - Multiple faces detected")
            
        for face in faces_dlib:
            results['face_detections'] += 1
            shape = predictor(frame, face)
            
            # Eye tracking
            left_eye = shape.part(36)
            right_eye = shape.part(45)
            nose_left = shape.part(31)
            nose_right = shape.part(35)
            
            eye_distance = abs(left_eye.x - right_eye.x)
            nose_distance = abs(nose_left.x - nose_right.x)
            
            if eye_distance < 0.6 * nose_distance:
                results['lookaway_count'] += 1
                logger.info(f"Frame {frame_number} - Lookaway detected (eye distance: {eye_distance}, nose distance: {nose_distance})")
                
        logger.debug(f"Frame {frame_number} results: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Frame {frame_number} analysis error: {str(e)}")
        return None

def compile_results(raw_results: Dict) -> Tuple[bool, Dict]:
    """Convert raw counts to final results with detailed statistics"""
    cheating_detected = False
    reasons = []
    
    # Calculate metrics
    total_frames = raw_results['total_frames']
    processed_frames = raw_results['processed_frames']
    processing_ratio = (processed_frames / total_frames) * 100 if total_frames > 0 else 0
    face_detection_rate = (raw_results['face_detections'] / processed_frames) * 100 if processed_frames > 0 else 0
    lookaway_ratio = (raw_results['lookaway_count'] / raw_results['face_detections']) if raw_results['face_detections'] > 0 else 0
    
    logger.info("\n" + "="*50)
    logger.info("VIDEO ANALYSIS SUMMARY")
    logger.info(f"Total frames: {total_frames}")
    logger.info(f"Processed frames: {processed_frames} ({processing_ratio:.1f}%)")
    logger.info(f"Face detection rate: {face_detection_rate:.1f}%")
    logger.info(f"Lookaway ratio: {lookaway_ratio:.2f}")
    logger.info("="*50 + "\n")
    
    # Cheating detection logic
    if raw_results.get('multiple_faces', False):
        cheating_detected = True
        reasons.append("Multiple faces detected")
        logger.warning("Cheating detected: Multiple faces in video")
    
    if processed_frames > 0:
        if face_detection_rate < 50:
            cheating_detected = True
            reasons.append(f"Low face detection rate ({face_detection_rate:.1f}%)")
            logger.warning(f"Cheating detected: Low face detection rate ({face_detection_rate:.1f}%)")
            
        if lookaway_ratio > 0.4:
            cheating_detected = True
            reasons.append(f"Excessive lookaways detected ({lookaway_ratio:.2f} ratio)")
            logger.warning(f"Cheating detected: Excessive lookaways ({lookaway_ratio:.2f} ratio)")
    
    return cheating_detected, {
        'reasons': reasons if reasons else ["No cheating detected"],
        'statistics': {
            'total_frames': total_frames,
            'processed_frames': processed_frames,
            'processing_ratio': f"{processing_ratio:.1f}%",
            'face_detection_rate': f"{face_detection_rate:.1f}%",
            'lookaway_ratio': f"{lookaway_ratio:.2f}",
            'multiple_faces_detected': raw_results.get('multiple_faces', False)
        },
        'raw_counts': {
            'face_detections': raw_results['face_detections'],
            'lookaway_count': raw_results['lookaway_count']
        }
    }

def is_video_valid(video_path: str) -> bool:
    """Validate video file can be opened and has frames with detailed checks"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Video {video_path} could not be opened")
            return False
            
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Video validation - Resolution: {width}x{height}, FPS: {fps:.2f}, Frames: {frame_count}")
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            logger.error("Video validation failed - Could not read first frame")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Video validation error: {str(e)}")
        return False

def analyze_video_keyframes(video_path: str, keyframe_interval: int = 30) -> Tuple[bool, Dict]:
    """Main analysis using keyframe extraction with comprehensive logging"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Failed to open video: {video_path}")
            return False, {'error': 'Could not open video file'}
            
        results = defaultdict(int)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        processed_frames = 0
        frame_counter = 0
        
        # Video properties log
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        logger.info("\n" + "="*50)
        logger.info(f"Starting analysis of {video_path}")
        logger.info(f"Resolution: {width}x{height}")
        logger.info(f"FPS: {fps:.2f}, Duration: {duration:.2f} seconds")
        logger.info(f"Total frames: {total_frames}, Keyframe interval: {keyframe_interval}")
        logger.info("="*50 + "\n")
        
        # Frame processing loop
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.info(f"Reached end of video at frame {frame_counter}")
                break
                
            frame_counter += 1
            
            # Only process keyframes
            if frame_counter % keyframe_interval != 0:
                continue
                
            logger.debug(f"\nProcessing frame {frame_counter}/{total_frames} ({(frame_counter/total_frames)*100:.1f}%)")
            
            frame_result = analyze_single_frame(frame, frame_counter)
            if frame_result:
                for k, v in frame_result.items():
                    if k != 'frame_number':
                        results[k] += v
                processed_frames += 1
                
                # Early termination if cheating detected
                if results.get('multiple_faces', False):
                    logger.warning(f"Early termination at frame {frame_counter} - Multiple faces detected")
                    break
                    
        cap.release()
        
        # Final results compilation
        results['total_frames'] = total_frames
        results['processed_frames'] = processed_frames
        
        logger.info("\n" + "="*50)
        logger.info("ANALYSIS COMPLETED")
        logger.info(f"Processed {processed_frames} keyframes ({processed_frames/total_frames*100:.1f}% of total)")
        logger.info(f"Face detections: {results['face_detections']}")
        logger.info(f"Lookaways detected: {results['lookaway_count']}")
        logger.info(f"Multiple faces detected: {'Yes' if results.get('multiple_faces', False) else 'No'}")
        logger.info("="*50 + "\n")
        
        return compile_results(results)
        
    except Exception as e:
        logger.error(f"Video analysis error: {str(e)}")
        return False, {'error': str(e)}

@app.route("/")
def home() -> str:
    return "AI Cheating Detection API (Keyframe Analysis Method)"

@app.route("/upload", methods=["POST"])
def upload_video() -> Tuple[Dict, int]:
    """Endpoint for video upload and analysis"""
    if "video" not in request.files:
        logger.error("No video file in upload request")
        return jsonify({"error": "No video file uploaded"}), 400

    video_file = request.files["video"]
    if video_file.filename == "":
        logger.error("Empty filename in upload request")
        return jsonify({"error": "Empty filename"}), 400

    try:
        # Save uploaded file
        video_path = os.path.join(app.config["UPLOAD_FOLDER"], video_file.filename)
        video_file.save(video_path)
        logger.info(f"Video saved to {video_path}")
        
        # Validate video
        if not is_video_valid(video_path):
            logger.error(f"Invalid video file: {video_path}")
            os.remove(video_path)
            return jsonify({"error": "Invalid video file"}), 400
            
        # Analyze video
        cheating_detected, details = analyze_video_keyframes(video_path)
        
        # Prepare response
        response = {
            "cheating_detected": cheating_detected,
            "details": details,
            "video_path": video_path,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Analysis completed for {video_path}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        if os.path.exists(video_path):
            os.remove(video_path)
        return jsonify({"error": f"Error processing video: {str(e)}"}), 500

if __name__ == "__main__":
    logger.info("Starting cheating detection API server")
    app.run(host='0.0.0.0', port=5000, threaded=True) 
    