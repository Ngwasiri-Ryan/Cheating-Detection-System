import cv2
import numpy as np
from typing import Optional, Tuple, Dict
import logging

logger = logging.getLogger(__name__)

def validate_and_convert_frame(frame: np.ndarray) -> Optional[np.ndarray]:
    """
    Ensure frame is in correct format for analysis.
    
    Args:
        frame: Input frame to validate
        
    Returns:
        Validated frame in RGB format or None if invalid
    """
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

def extract_face_region(frame: np.ndarray, face_coords: Tuple[int, int, int, int], 
                       padding: int = 20) -> Optional[np.ndarray]:
    """
    Extract face region from frame with padding.
    
    Args:
        frame: Input frame
        face_coords: (x, y, w, h) face coordinates
        padding: Pixels to pad around face
        
    Returns:
        Extracted face region or None if invalid
    """
    try:
        x, y, w, h = face_coords
        height, width = frame.shape[:2]
        
        # Apply padding with boundary checks
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(width, x + w + padding)
        y2 = min(height, y + h + padding)
        
        face_region = frame[y1:y2, x1:x2]
        return face_region
    except Exception as e:
        logger.error(f"Face extraction failed: {str(e)}")
        return None