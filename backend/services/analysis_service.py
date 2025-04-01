import logging
from typing import Dict, Tuple, Optional
from datetime import datetime
from collections import defaultdict
from core.detection import CheatingDetector
from core.video_processor import VideoProcessor
from services.file_service import FileService
from core.exceptions import (
    VideoValidationError,
    VideoProcessingError,
    AnalysisServiceError
)

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self, video_processor: VideoProcessor, file_service: FileService):
        """
        Initialize analysis service with dependencies.
        
        Args:
            video_processor: Configured VideoProcessor instance
            file_service: Configured FileService instance
        """
        self.video_processor = video_processor
        self.file_service = file_service
        self.analysis_history = defaultdict(dict)

    def analyze_video(self, video_file) -> Tuple[bool, Dict]:
        """
        Complete video analysis workflow.
        
        Args:
            video_file: File object or path to video
            
        Returns:
            Tuple: (cheating_detected, analysis_details)
            
        Raises:
            AnalysisServiceError: If analysis fails
        """
        try:
            # 1. Save uploaded file
            video_path = self.file_service.save_uploaded_file(video_file)
            logger.info(f"Video saved to {video_path}")
            
            # 2. Process video
            cheating_detected, analysis_details = self.video_processor.process_video(video_path)
            
            # 3. Record analysis
            self._record_analysis(
                video_path=video_path,
                timestamp=datetime.now(),
                result=cheating_detected,
                details=analysis_details
            )
            
            return cheating_detected, analysis_details
            
        except VideoValidationError as e:
            logger.error(f"Video validation failed: {str(e)}")
            raise AnalysisServiceError(f"Invalid video: {str(e)}")
        except VideoProcessingError as e:
            logger.error(f"Video processing failed: {str(e)}")
            raise AnalysisServiceError(f"Processing error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected analysis error: {str(e)}")
            raise AnalysisServiceError(f"Analysis failed: {str(e)}")

    def _record_analysis(self, video_path: str, timestamp: datetime, 
                       result: bool, details: Dict) -> None:
        """
        Record analysis results in history.
        
        Args:
            video_path: Path to analyzed video
            timestamp: Analysis timestamp
            result: Cheating detection result
            details: Full analysis details
        """
        video_id = self.file_service.get_file_id(video_path)
        self.analysis_history[video_id] = {
            'timestamp': timestamp.isoformat(),
            'video_path': video_path,
            'result': result,
            'details': details
        }
        logger.debug(f"Recorded analysis for {video_id}")

    def get_analysis_history(self, video_id: Optional[str] = None) -> Dict:
        """
        Retrieve analysis history.
        
        Args:
            video_id: Optional specific video ID
            
        Returns:
            Dictionary of analysis records
        """
        if video_id:
            return self.analysis_history.get(video_id, {})
        return dict(self.analysis_history)

    def get_analysis_stats(self) -> Dict:
        """
        Calculate analysis statistics.
        
        Returns:
            Dictionary of summary statistics
        """
        total = len(self.analysis_history)
        cheating_count = sum(1 for v in self.analysis_history.values() if v['result'])
        
        return {
            'total_analyses': total,
            'cheating_detected': cheating_count,
            'cheating_percentage': (cheating_count / total * 100) if total > 0 else 0,
            'last_analysis': max(
                (v['timestamp'] for v in self.analysis_history.values()),
                default=None
            )
        }