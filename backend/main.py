from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import os
from typing import Tuple, Dict
import cv2
import dlib

# Corrected imports without 'backend' prefix
from core.detection import CheatingDetector
from core.video_processor import VideoProcessor
from services.file_service import FileService
from config import Config
from core.exceptions import (
    ModelLoadingError,
    VideoValidationError,
    VideoProcessingError,
    FileSystemError
)
from chatbot.core.chatbot import Chatbot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/cheating_detection_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app(config: Config) -> Flask:
    app = Flask(__name__)
    CORS(app)
    chatbot = Chatbot()
    
    try:
        # Initialize ML models
        face_cascade = cv2.CascadeClassifier(config.FACE_CASCADE_PATH)
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(config.LANDMARK_PREDICTOR_PATH)
        
        # Create core components
        cheating_detector = CheatingDetector(face_cascade, detector, predictor)
        video_processor = VideoProcessor(cheating_detector, {
            'keyframe_interval': config.KEYFRAME_INTERVAL,
            'min_face_detection_rate': config.FACE_DETECTION_THRESHOLD,
            'lookaway_ratio_threshold': config.LOOKAWAY_THRESHOLD
        })
        file_service = FileService(config.UPLOAD_FOLDER)
        
    except Exception as e:
        logger.critical(f"Failed to initialize services: {str(e)}")
        raise ModelLoadingError("Initialization failed", str(e))

    @app.route("/")
    def home() -> str:
        return "AI Cheating Detection API"

    @app.route('/api/chat', methods=['POST'])
    def chat():
     data = request.get_json()
     if not data or 'message' not in data:
             return jsonify({"error": "Message required"}), 400
     return jsonify(chatbot.get_response(data['message']))

    @app.route("/upload", methods=["POST"])
    def upload_video() -> Tuple[Dict, int]:
        if "video" not in request.files:
            return jsonify({"error": "No video file uploaded"}), 400

        video_file = request.files["video"]
        if video_file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        try:
            video_path = file_service.save_uploaded_file(video_file)
            cheating_detected, details = video_processor.process_video(video_path)
            
            return jsonify({
                "cheating_detected": cheating_detected,
                "details": details,
                "video_path": video_path,
                "timestamp": datetime.now().isoformat()
            })
            
        except VideoValidationError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == "__main__":
    config = Config()
    os.makedirs("logs", exist_ok=True)
    app = create_app(config)
    app.run(host='0.0.0.0', port=5000)