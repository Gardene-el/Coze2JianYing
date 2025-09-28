"""
Coze Plugin Tool: Get Media Duration

This tool analyzes audio/video files from URLs and returns timeline information
including individual and cumulative durations.
"""

import os
import tempfile
import requests
from typing import List, Dict, Any
from urllib.parse import urlparse
import json

# Import pymediainfo for media analysis
try:
    from pymediainfo import MediaInfo
except ImportError:
    MediaInfo = None

from runtime import Args
from typings.get_media_duration.get_media_duration import Input, Output


def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def check_media_url_accessibility(url: str, timeout: int = 10) -> dict:
    """
    Check if a media URL is accessible and get basic info
    
    Args:
        url: Media file URL
        timeout: Request timeout
        
    Returns:
        Dict with accessibility info and content details
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*'
        }
        
        # Add CDN-specific headers
        if 'oceancloudapi.com' in url or 'volccdn.com' in url or 'bytedance.com' in url:
            headers['Referer'] = 'https://www.coze.cn/'
            headers['Origin'] = 'https://www.coze.cn'
        
        response = requests.head(url, headers=headers, timeout=timeout)
        
        return {
            'accessible': response.status_code == 200,
            'status_code': response.status_code,
            'content_type': response.headers.get('content-type', 'unknown'),
            'content_length': response.headers.get('content-length'),
            'headers': dict(response.headers)
        }
    except Exception as e:
        return {
            'accessible': False,
            'error': str(e),
            'status_code': None
        }


def download_media_file(url: str, timeout: int = 30) -> str:
    """
    Download media file to temporary location for analysis
    
    Args:
        url: Media file URL
        timeout: Download timeout in seconds
        
    Returns:
        Path to downloaded temporary file
        
    Raises:
        Exception: If download fails
    """
    if not validate_url(url):
        raise ValueError(f"Invalid URL: {url}")
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tmp')
    temp_path = temp_file.name
    temp_file.close()
    
    try:
        # Try downloading with different header strategies
        success = False
        last_error = None
        
        # Strategy 1: Comprehensive modern browser headers
        headers_strategies = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'audio/*,video/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                'Accept-Encoding': 'identity',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'audio',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"'
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'identity'
            },
            {
                'User-Agent': 'curl/7.68.0',
                'Accept': '*/*'
            }
        ]
        
        for i, base_headers in enumerate(headers_strategies):
            try:
                headers = base_headers.copy()
                
                # Add CDN-specific headers based on URL
                if 'oceancloudapi.com' in url or 'volccdn.com' in url or 'bytedance.com' in url:
                    headers['Referer'] = 'https://www.coze.cn/'
                    headers['Origin'] = 'https://www.coze.cn'
                elif 'amazonaws.com' in url or 'cloudfront.net' in url:
                    headers['Referer'] = 'https://aws.amazon.com/'
                elif 'googleapis.com' in url or 'gstatic.com' in url:
                    headers['Referer'] = 'https://cloud.google.com/'
                
                response = requests.get(url, headers=headers, timeout=timeout, stream=True)
                response.raise_for_status()
                
                # If we get here, download was successful
                success = True
                break
                
            except requests.exceptions.RequestException as e:
                last_error = e
                if i < len(headers_strategies) - 1:
                    continue  # Try next strategy
                else:
                    break  # All strategies failed
        
        if not success:
            raise last_error or Exception("All download strategies failed")
        
        # Write to temporary file
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return temp_path
        
    except Exception as e:
        # Clean up temporary file on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        
        # Provide more specific error messages
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg:
            raise Exception(f"Access denied to {url}. This may be a signed URL that requires specific authentication or has expired. Original error: {error_msg}")
        elif "404" in error_msg or "Not Found" in error_msg:
            raise Exception(f"Media file not found at {url}. Please verify the URL is correct and accessible.")
        elif "timeout" in error_msg.lower():
            raise Exception(f"Download timeout for {url}. The file may be too large or the server is slow to respond.")
        else:
            raise Exception(f"Failed to download {url}: {error_msg}")


def get_media_duration_ms(file_path: str) -> int:
    """
    Get media duration in milliseconds using pymediainfo
    
    Args:
        file_path: Path to media file
        
    Returns:
        Duration in milliseconds
        
    Raises:
        Exception: If duration cannot be determined
    """
    if not MediaInfo:
        raise Exception("pymediainfo is not available")
    
    if not os.path.exists(file_path):
        raise Exception(f"File not found: {file_path}")
    
    try:
        media_info = MediaInfo.parse(file_path)
        
        # Look for duration in video or audio tracks
        duration_ms = None
        
        for track in media_info.tracks:
            if track.track_type in ['Video', 'Audio', 'General']:
                if hasattr(track, 'duration') and track.duration:
                    duration_ms = int(float(track.duration))
                    break
        
        if duration_ms is None:
            raise Exception("Could not determine media duration")
            
        return duration_ms
        
    except Exception as e:
        raise Exception(f"Failed to analyze media file: {str(e)}")


def cleanup_temp_file(file_path: str):
    """Safely remove temporary file"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception:
        pass  # Ignore cleanup errors


def handler(args: Args) -> Output:
    """
    Main handler function for getting media duration
    
    Args:
        args: Input arguments containing links array
        
    Returns:
        Output containing all_timelines and timelines data
    """
    links = args.input.links
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Processing {len(links)} media links")
    
    if not links:
        return Output(
            all_timelines=[],
            timelines=[]
        )
    
    durations = []
    temp_files = []
    
    try:
        # Process each URL
        for i, url in enumerate(links):
            if logger:
                logger.info(f"Processing link {i+1}/{len(links)}: {url}")
            
            try:
                # First check URL accessibility for better error reporting
                if logger:
                    logger.info(f"Checking accessibility of {url}")
                
                access_info = check_media_url_accessibility(url)
                if not access_info['accessible']:
                    error_detail = f"URL not accessible (status: {access_info.get('status_code', 'unknown')})"
                    if 'error' in access_info:
                        error_detail += f". Error: {access_info['error']}"
                    
                    if logger:
                        logger.warning(f"Skipping {url}: {error_detail}")
                    continue
                
                if logger:
                    content_type = access_info.get('content_type', 'unknown')
                    logger.info(f"URL accessible, content-type: {content_type}")
                
                # Download file temporarily
                temp_path = download_media_file(url)
                temp_files.append(temp_path)
                
                # Get duration
                duration_ms = get_media_duration_ms(temp_path)
                durations.append(duration_ms)
                
                if logger:
                    logger.info(f"Duration for {url}: {duration_ms}ms")
                    
            except Exception as e:
                error_msg = f"Error processing {url}: {str(e)}"
                if logger:
                    logger.error(error_msg)
                # For failed files, we'll skip them rather than fail entirely
                continue
        
        # Calculate timelines
        if not durations:
            return Output(
                all_timelines=[],
                timelines=[]
            )
        
        # Calculate cumulative timelines
        timelines = []
        current_start = 0
        
        for duration in durations:
            timeline = {
                "start": current_start,
                "end": current_start + duration
            }
            timelines.append(timeline)
            current_start += duration
        
        # Total timeline
        total_duration = sum(durations)
        all_timelines = [{"start": 0, "end": total_duration}]
        
        if logger:
            logger.info(f"Generated {len(timelines)} individual timelines, total duration: {total_duration}ms")
        
        return Output(
            all_timelines=all_timelines,
            timelines=timelines
        )
        
    except Exception as e:
        error_msg = f"Unexpected error in handler: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        # Return empty result on critical error
        return Output(
            all_timelines=[],
            timelines=[]
        )
        
    finally:
        # Clean up all temporary files
        for temp_file in temp_files:
            cleanup_temp_file(temp_file)

