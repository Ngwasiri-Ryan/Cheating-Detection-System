class CheatingDetectionError(Exception):
    """Base exception for cheating detection errors"""
    def __init__(self, message: str, error_code: int = 1000):
        super().__init__(message)
        self.error_code = error_code
        self.message = message

    def __str__(self):
        return f"[Error {self.error_code}] {self.message}"

class ModelLoadingError(CheatingDetectionError):
    """Raised when model loading fails"""
    def __init__(self, model_name: str, details: str = ""):
        message = f"Failed to load model: {model_name}"
        if details:
            message += f" - {details}"
        super().__init__(message, error_code=1001)

class VideoValidationError(CheatingDetectionError):
    """Raised when video validation fails"""
    def __init__(self, video_path: str, reason: str):
        message = f"Invalid video '{video_path}': {reason}"
        super().__init__(message, error_code=2000)

class VideoProcessingError(CheatingDetectionError):
    """Raised when video processing fails"""
    def __init__(self, video_path: str, frame_number: int = None, details: str = ""):
        message = f"Error processing '{video_path}'"
        if frame_number is not None:
            message += f" at frame {frame_number}"
        if details:
            message += f": {details}"
        super().__init__(message, error_code=2001)
        
        

class FrameAnalysisError(CheatingDetectionError):
    """Raised when frame analysis fails"""
    def __init__(self, frame_number: int, details: str = ""):
        message = f"Frame analysis failed at frame {frame_number}"
        if details:
            message += f": {details}"
        super().__init__(message, error_code=3000)
        
class FileSystemError(Exception):
    """Exception raised for filesystem-related errors in the cheating detection system.
    
    Attributes:
        operation: The filesystem operation being attempted
        path: The file path involved in the operation
        message: Explanation of the error
        error_code: Numeric code for error classification
    """
    
    def __init__(self, operation: str, path: str, message: str = "", error_code: int = 5000):
        """Initialize FileSystemError with operation details.
        
        Args:
            operation: Filesystem operation being performed (e.g., 'save', 'delete')
            path: File path involved in the operation
            message: Optional detailed error message
            error_code: Numeric error code for classification
        """
        self.operation = operation
        self.path = path
        self.error_code = error_code
        self.message = message or f"Filesystem error during {operation} operation"
        super().__init__(self.message)

    def __str__(self):
        """String representation of the error."""
        return (f"[Error {self.error_code}] {self.message} "
               f"(operation: {self.operation}, path: {self.path})")

    def to_dict(self) -> dict:
        """Convert error details to dictionary for API responses.
        
        Returns:
            Dictionary containing error details
        """
        return {
            'error_type': 'FileSystemError',
            'error_code': self.error_code,
            'operation': self.operation,
            'path': self.path,
            'message': self.message
        }
        
class AnalysisServiceError(CheatingDetectionError):
    """Raised when analysis service operations fail"""
    def __init__(self, service_method: str, resource: str = None, details: str = ""):
        """
        Initialize analysis service error
        
        Args:
            service_method: The service method that failed (e.g., 'analyze_video')
            resource: The resource being processed (e.g., video path)
            details: Technical details about the failure
        """
        message = f"Analysis service error in '{service_method}'"
        if resource:
            message += f" for resource '{resource}'"
        if details:
            message += f": {details}"
            
        super().__init__(message, error_code=4000)
        
        self.service_method = service_method
        self.resource = resource
        self.details = details

    def to_dict(self) -> dict:
        """Convert error to dictionary for API responses"""
        return {
            'error_type': 'AnalysisServiceError',
            'error_code': self.error_code,
            'service_method': self.service_method,
            'resource': self.resource,
            'message': self.message,
            'details': self.details
        }
        
    def __init__(self, operation: str, stage: str = "", details: str = ""):
        """
        Initialize analysis service error
        
        Args:
            operation: The analysis operation being performed
            stage: Which stage of analysis failed (e.g., 'frame_processing')
            details: Technical details about the failure
        """
        message = f"Analysis service failed during {operation}"
        if stage:
            message += f" at stage: {stage}"
        if details:
            message += f" (Details: {details})"
            
        super().__init__(message, error_code=4000)
        
        self.operation = operation
        self.stage = stage
        self.details = details

    def to_dict(self) -> dict:
        """Convert error to dictionary for API responses"""
        return {
            'error_type': 'AnalysisServiceError',
            'error_code': self.error_code,
            'operation': self.operation,
            'stage': self.stage,
            'message': self.message,
            'details': self.details
        }