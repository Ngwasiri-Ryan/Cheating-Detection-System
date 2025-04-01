import cv2
import dlib
import numpy as np
from typing import Dict, Tuple, Optional
import logging
from core.exceptions import FrameAnalysisError

logger = logging.getLogger(__name__)

class CheatingDetector:
    def __init__(self, face_cascade, detector, predictor):
        """
        Initialize cheating detector with required models.
        
        Args:
            face_cascade: OpenCV face cascade classifier
            detector: dlib face detector
            predictor: dlib facial landmark predictor
        """
        self.face_cascade = face_cascade
        self.detector = detector
        self.predictor = predictor

    def analyze_frame(self, frame: np.ndarray, frame_number: int) -> Dict:
        """
        Analyze a single frame for cheating indicators.
        
        Args:
            frame: Video frame to analyze
            frame_number: Frame number for reference
            
        Returns:
            Dictionary containing analysis results
            
        Raises:
            FrameAnalysisError: If frame analysis fails
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            results = {
                'face_detections': 0,
                'lookaway_count': 0,
                'multiple_faces': False,
                'frame_number': frame_number
            }
            
            # OpenCV face detection
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            # dlib face detection
            faces_dlib = self.detector(frame, 1)
            
            logger.debug(f"Frame {frame_number} - OpenCV faces: {len(faces)}, dlib faces: {len(faces_dlib)}")
            
            # Check for multiple faces
            if len(faces) > 1 or len(faces_dlib) > 1:
                results['multiple_faces'] = True
                logger.warning(f"Multiple faces detected in frame {frame_number}")
                
            # Analyze each face
            for face in faces_dlib:
                results['face_detections'] += 1
                shape = self.predictor(frame, face)
                
                # Eye tracking for lookaway detection
                left_eye = shape.part(36)
                right_eye = shape.part(45)
                nose_left = shape.part(31)
                nose_right = shape.part(35)
                
                eye_distance = abs(left_eye.x - right_eye.x)
                nose_distance = abs(nose_left.x - nose_right.x)
                
                if eye_distance < 0.6 * nose_distance:
                    results['lookaway_count'] += 1
                    logger.debug(f"Lookaway detected in frame {frame_number}")
                    
            return results
            
        except Exception as e:
            logger.error(f"Frame analysis failed: {str(e)}")
            raise FrameAnalysisError(frame_number, str(e))

    def compile_results(self, raw_results: Dict) -> Tuple[bool, Dict]:
        """
        Compile frame-level results into final analysis.
        
        Args:
            raw_results: Accumulated results from frame analysis
            
        Returns:
            Tuple: (cheating_detected, analysis_details)
        """
        cheating_detected = False
        reasons = []
        
        # Calculate metrics
        total_frames = raw_results['total_frames']
        processed_frames = raw_results['processed_frames']
        processing_ratio = (processed_frames / total_frames) * 100 if total_frames > 0 else 0
        face_detection_rate = (raw_results['face_detections'] / processed_frames) * 100 if processed_frames > 0 else 0
        lookaway_ratio = (raw_results['lookaway_count'] / raw_results['face_detections']) if raw_results['face_detections'] > 0 else 0
        
        # Detection logic
        if raw_results.get('multiple_faces', False):
            cheating_detected = True
            reasons.append("Multiple faces detected")
            
        if processed_frames > 0:
            if face_detection_rate < 50:
                cheating_detected = True
                reasons.append(f"Low face detection rate ({face_detection_rate:.1f}%)")
                
            if lookaway_ratio > 0.4:
                cheating_detected = True
                reasons.append(f"Excessive lookaways ({lookaway_ratio:.2f} ratio)")
        
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
            'raw_counts': raw_results
        }