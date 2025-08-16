import os
import sys
import ffmpeg
from typing import List, Optional
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import get_video_file_path, get_processed_video_path, ensure_temp_directories

class VideoService:
    """
    Video processing service using FFmpeg
    Handles video merging and processing operations
    """
    
    def __init__(self):
        ensure_temp_directories()
    
    def merge_videos(
        self, 
        video_paths: List[str], 
        output_video_id: int,
        output_format: str = "mp4"
    ) -> str:
        """
        Merge multiple video files into one
        
        Args:
            video_paths: List of paths to video files to merge
            output_video_id: ID for the output video file
            output_format: Output video format (default: mp4)
            
        Returns:
            Path to the merged video file
        """
        if not video_paths:
            raise ValueError("At least one video path is required")
        
        # Validate input files exist
        for path in video_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Video file not found: {path}")
        
        # Generate output path
        output_path = get_processed_video_path(output_video_id, output_format)
        
        try:
            # Create input streams
            inputs = [ffmpeg.input(path) for path in video_paths]
            
            # Concatenate videos
            if len(inputs) == 1:
                # Single video, just copy
                stream = inputs[0]
            else:
                # Multiple videos, concatenate
                stream = ffmpeg.concat(*inputs, v=1, a=1)
            
            # Output with video and audio codecs
            stream = ffmpeg.output(
                stream, 
                output_path,
                vcodec='libx264',
                acodec='aac',
                **{'b:v': '1000k', 'b:a': '128k'}
            )
            
            # Run the ffmpeg command
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error during video merge: {e}")
    
    def merge_videos_with_transition(
        self,
        video_paths: List[str],
        output_video_id: int,
        transition_duration: float = 0.5,
        output_format: str = "mp4"
    ) -> str:
        """
        Merge videos with crossfade transitions
        
        Args:
            video_paths: List of paths to video files to merge
            output_video_id: ID for the output video file
            transition_duration: Duration of crossfade transition in seconds
            output_format: Output video format
            
        Returns:
            Path to the merged video file with transitions
        """
        if len(video_paths) < 2:
            return self.merge_videos(video_paths, output_video_id, output_format)
        
        # Validate input files
        for path in video_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Video file not found: {path}")
        
        output_path = get_processed_video_path(output_video_id, output_format)
        
        try:
            # For complex transitions, we'll use a simpler approach
            # Create input streams
            inputs = [ffmpeg.input(path) for path in video_paths]
            
            # For now, do simple concatenation
            # TODO: Implement crossfade transitions in future iterations
            stream = ffmpeg.concat(*inputs, v=1, a=1)
            
            stream = ffmpeg.output(
                stream,
                output_path,
                vcodec='libx264',
                acodec='aac',
                **{'b:v': '1000k', 'b:a': '128k'}
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error during video merge with transitions: {e}")
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Get video file information (duration, resolution, etc.)
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing video information
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
            
            info = {
                'duration': float(probe['format']['duration']),
                'size': int(probe['format']['size']),
                'format': probe['format']['format_name']
            }
            
            if video_stream:
                info.update({
                    'width': int(video_stream['width']),
                    'height': int(video_stream['height']),
                    'video_codec': video_stream['codec_name'],
                    'fps': eval(video_stream['r_frame_rate'])
                })
            
            if audio_stream:
                info.update({
                    'audio_codec': audio_stream['codec_name'],
                    'sample_rate': int(audio_stream['sample_rate'])
                })
            
            return info
            
        except ffmpeg.Error as e:
            raise RuntimeError(f"Error getting video info: {e}")

# Create global video service instance
video_service = VideoService()