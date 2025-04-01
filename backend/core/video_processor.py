import cv2
from typing import Tuple, Dict, Optional
from collections import defaultdict
import logging
from .exceptions import VideoValidationError, VideoProcessingError

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, cheating_detector, config: Optional[Dict] = None):
        """
        Initialize video processor with cheating detector.
        
        Args:
            cheating_detector: CheatingDetector instance
            config: Processing configuration
        """
        self.detector = cheating_detector
        self.config = {
            'keyframe_interval': 30,
            'min_face_detection_rate': 50,
            'lookaway_ratio_threshold': 0.4,
            'early_termination': True
        }
        if config:
            self.config.update(config)

    def process_video(self, video_path: str) -> Tuple[bool, Dict]:
        """
        Process video and detect cheating indicators.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Tuple: (cheating_detected, analysis_details)
            
        Raises:
            VideoProcessingError: If processing fails
        """
        try:
            # Validate video first
            self._validate_video(video_path)
            
            cap = cv2.VideoCapture(video_path)
            results = defaultdict(int)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            processed_frames = 0
            frame_counter = 0
            
            # Process frames
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                frame_counter += 1
                
                # Only process keyframes
                if frame_counter % self.config['keyframe_interval'] != 0:
                    continue
                    
                # Analyze frame
                frame_result = self.detector.analyze_frame(frame, frame_counter)
                if frame_result:
                    for k, v in frame_result.items():
                        if k != 'frame_number':
                            results[k] += v
                    processed_frames += 1
                    
                    # Early termination if cheating detected
                    if self.config['early_termination'] and results.get('multiple_faces', False):
                        break
                        
            cap.release()
            
            # Compile final results
            results['total_frames'] = total_frames
            results['processed_frames'] = processed_frames
            
            return self.detector.compile_results(results)
            
        except VideoValidationError:
            raise
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            raise VideoProcessingError(video_path, frame_counter, str(e))

    def _validate_video(self, video_path: str) -> None:
        """
        Validate video file can be processed.
        
        Args:
            video_path: Path to video file
            
        Raises:
            VideoValidationError: If video is invalid
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise VideoValidationError(video_path, "Could not open video file")
            
        if int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) == 0:
            cap.release()
            raise VideoValidationError(video_path, "Video has no frames")
            
        cap.release()