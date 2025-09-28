"""
Media Models for Coze Plugin Tools

Data structures for handling media files and their metadata,
specifically designed for Coze platform constraints and media processing workflows.
"""

from typing import List, Dict, Optional, NamedTuple
from dataclasses import dataclass


@dataclass
class MediaTimeline:
    """Represents a timeline segment with start and end times in milliseconds"""
    start: int  # Start time in milliseconds
    end: int    # End time in milliseconds
    
    @property
    def duration(self) -> int:
        """Get duration in milliseconds"""
        return self.end - self.start
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary format for JSON serialization"""
        return {"start": self.start, "end": self.end}


@dataclass 
class MediaInfo:
    """Media file information including URL and duration"""
    url: str                    # Original URL
    duration_ms: int           # Duration in milliseconds
    file_size: Optional[int] = None    # File size in bytes (if available)
    format: Optional[str] = None       # Media format (mp4, mp3, etc.)
    error: Optional[str] = None        # Error message if processing failed


@dataclass
class MediaDurationResult:
    """Result structure for media duration analysis"""
    all_timelines: List[Dict[str, int]]  # Total timeline information
    timelines: List[Dict[str, int]]      # Individual file timelines
    processed_count: int = 0             # Number of successfully processed files
    failed_count: int = 0                # Number of failed files
    total_duration_ms: int = 0           # Total duration in milliseconds
    
    @classmethod
    def from_durations(cls, durations: List[int]) -> 'MediaDurationResult':
        """Create result from list of durations in milliseconds"""
        if not durations:
            return cls(all_timelines=[], timelines=[])
        
        # Calculate individual timelines
        timelines = []
        current_start = 0
        
        for duration in durations:
            timeline = {"start": current_start, "end": current_start + duration}
            timelines.append(timeline)
            current_start += duration
        
        # Calculate total timeline
        total_duration = sum(durations)
        all_timelines = [{"start": 0, "end": total_duration}]
        
        return cls(
            all_timelines=all_timelines,
            timelines=timelines,
            processed_count=len(durations),
            total_duration_ms=total_duration
        )


class MediaProcessingInput(NamedTuple):
    """Input structure for media processing tools"""
    links: List[str]  # List of media URLs to process


class MediaProcessingOutput(NamedTuple):
    """Output structure for media processing tools"""
    all_timelines: List[Dict[str, int]]  # Total timeline
    timelines: List[Dict[str, int]]      # Individual timelines


# Legacy compatibility for existing tools
Input = MediaProcessingInput
Output = MediaProcessingOutput


# Utility functions for working with media models

def validate_media_url(url: str) -> bool:
    """
    Validate if a URL appears to be a valid media URL
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL appears valid
    """
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_supported_media_format(url: str) -> bool:
    """
    Check if URL points to a supported media format
    
    Args:
        url: Media URL to check
        
    Returns:
        True if format appears to be supported
    """
    supported_extensions = {
        # Video formats
        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v',
        # Audio formats  
        '.mp3', '.wav', '.aac', '.ogg', '.flac', '.m4a', '.wma'
    }
    
    url_lower = url.lower()
    return any(url_lower.endswith(ext) for ext in supported_extensions)


def calculate_cumulative_timelines(durations_ms: List[int]) -> List[MediaTimeline]:
    """
    Calculate cumulative timelines from a list of durations
    
    Args:
        durations_ms: List of durations in milliseconds
        
    Returns:
        List of MediaTimeline objects with cumulative start/end times
    """
    timelines = []
    current_start = 0
    
    for duration in durations_ms:
        timeline = MediaTimeline(start=current_start, end=current_start + duration)
        timelines.append(timeline)
        current_start += duration
    
    return timelines


def format_duration(duration_ms: int) -> str:
    """
    Format duration in milliseconds to human-readable string
    
    Args:
        duration_ms: Duration in milliseconds
        
    Returns:
        Formatted duration string (e.g., "1m 23.5s")
    """
    if duration_ms < 1000:
        return f"{duration_ms}ms"
    
    seconds = duration_ms / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds:.1f}s"
    
    hours = int(minutes // 60)
    remaining_minutes = minutes % 60
    return f"{hours}h {remaining_minutes}m {remaining_seconds:.1f}s"