import os
import cv2
from pathlib import Path

class Config:
    # Directory names (relative to package root)
    UPLOAD_FOLDER = "uploads"
    MODEL_FOLDER = "models"
    LOG_FOLDER = "logs"
    
    # Initialize paths (will be set in __init__)
    FACE_CASCADE_PATH = ""
    LANDMARK_PREDICTOR_PATH = ""
    
    # Analysis parameters
    KEYFRAME_INTERVAL = 60
    LOOKAWAY_THRESHOLD = 0.6
    FACE_DETECTION_THRESHOLD = 0.3

    def __init__(self):
        """Initialize configuration with proper absolute paths"""
        # Get package root directory
        self.PACKAGE_ROOT = Path(__file__).parent
        
        # Create required directories
        self.UPLOAD_FOLDER = self._ensure_dir(self.UPLOAD_FOLDER)
        self.MODEL_FOLDER = self._ensure_dir(self.MODEL_FOLDER)
        self.LOG_FOLDER = self._ensure_dir(self.LOG_FOLDER)
        
        # Set model paths
        self.FACE_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.LANDMARK_PREDICTOR_PATH = str(self.MODEL_FOLDER / "shape_predictor_68_face_landmarks.dat")
        
        # Validate paths
        self.validate_paths()

    def _ensure_dir(self, dir_name):
        """Ensure directory exists and return absolute path"""
        path = self.PACKAGE_ROOT / dir_name
        path.mkdir(exist_ok=True)
        return path

    def validate_paths(self):
        """Validate that all required files exist"""
        if not Path(self.FACE_CASCADE_PATH).exists():
            raise FileNotFoundError(f"Face cascade not found at {self.FACE_CASCADE_PATH}")
        
        if not Path(self.LANDMARK_PREDICTOR_PATH).exists():
            raise FileNotFoundError(
                f"Dlib shape predictor not found at {self.LANDMARK_PREDICTOR_PATH}\n"
                "Please download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2\n"
                "Extract and place in models/ directory"
            )
        return True