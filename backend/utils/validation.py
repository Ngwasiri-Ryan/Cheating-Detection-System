import os
import cv2
from typing import Dict, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def validate_video_file(video_path: str) -> Tuple[bool, Dict]:
    """
    Validate video file can be opened and has frames.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Tuple: (is_valid, video_metadata) containing validation result and video properties
    """
    try:
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return False, {'error': 'File not found'}
            
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return False, {'error': 'Could not open video file'}
            
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        metadata = {
            'width': width,
            'height': height,
            'fps': fps,
            'frame_count': frame_count,
            'duration': duration,
            'valid': True
        }
        
        logger.info(f"Video validated: {metadata}")
        return True, metadata
        
    except Exception as e:
        logger.error(f"Video validation error: {str(e)}")
        return False, {'error': str(e)}

def validate_config(config: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple: (is_valid, error_message)
    """
    required_keys = {
        'UPLOAD_FOLDER': str,
        'KEYFRAME_INTERVAL': int,
        'FACE_DETECTION_THRESHOLD': (int, float),
        'LOOKAWAY_THRESHOLD': (int, float)
    }
    
    for key, expected_type in required_keys.items():
        if key not in config:
            return False, f"Missing required config key: {key}"
            
        if not isinstance(config[key], expected_type):
            return False, f"Invalid type for {key}. Expected {expected_type}"
            
    # Validate paths
    try:
        Path(config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, f"Could not create upload directory: {str(e)}"
        
    return True, None