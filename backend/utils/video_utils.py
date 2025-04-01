import cv2
import numpy as np
from typing import List, Optional, Dict, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def extract_keyframes(video_path: str, interval: int = 30) -> Tuple[List[np.ndarray], Dict]:
    """
    Extract keyframes from video at specified interval.
    
    Args:
        video_path: Path to video file
        interval: Extract every Nth frame
        
    Returns:
        Tuple: (frames, metadata) containing list of keyframes and video metadata
    """
    frames = []
    metadata = {}
    
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return frames, {'error': 'Could not open video file'}
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        metadata = {
            'total_frames': total_frames,
            'fps': fps,
            'duration': total_frames / fps if fps > 0 else 0,
            'keyframe_count': 0
        }
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_idx % interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
                
            frame_idx += 1
            
        cap.release()
        metadata['keyframe_count'] = len(frames)
        logger.info(f"Extracted {len(frames)} keyframes from {video_path}")
        return frames, metadata
        
    except Exception as e:
        logger.error(f"Keyframe extraction failed: {str(e)}")
        return frames, {'error': str(e)}

def calculate_video_metrics(video_path: str) -> Dict:
    """
    Calculate basic video metrics without processing frames.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary containing video metrics
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {'error': 'Could not open video file'}
            
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            'width': width,
            'height': height,
            'fps': fps,
            'frame_count': frame_count,
            'duration': duration,
            'valid': True
        }
    except Exception as e:
        return {'error': str(e)}

def generate_video_thumbnail(video_path: str, output_path: Optional[str] = None, 
                           frame_time: float = 1.0) -> Optional[np.ndarray]:
    """
    Generate thumbnail from video at specified time.
    
    Args:
        video_path: Path to video file
        output_path: Optional path to save thumbnail
        frame_time: Time in seconds to capture thumbnail
        
    Returns:
        Thumbnail image as numpy array or None if failed
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_pos = int(fps * frame_time)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return None
            
        thumbnail = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        if output_path:
            cv2.imwrite(output_path, cv2.cvtColor(thumbnail, cv2.COLOR_RGB2BGR))
            
        return thumbnail
    except Exception as e:
        logger.error(f"Thumbnail generation failed: {str(e)}")
        return None