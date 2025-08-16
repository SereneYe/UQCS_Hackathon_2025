import os
import sys
import ffmpeg
from typing import Optional
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import get_video_file_path, get_processed_video_path, ensure_temp_directories

class AudioVideoService:
    """
    Audio-Video processing service using FFmpeg
    Handles merging audio with video files
    """
    
    def __init__(self):
        ensure_temp_directories()
    
    def merge_audio_with_video(
        self,
        video_path: str,
        audio_path: str,
        output_video_id: int,
        audio_start_time: float = 0.0,
        video_start_time: float = 0.0,
        output_format: str = "mp4"
    ) -> str:
        """
        Merge audio file with video file
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_video_id: ID for the output video file
            audio_start_time: Start time for audio in seconds (default: 0.0)
            video_start_time: Start time for video in seconds (default: 0.0)
            output_format: Output video format (default: mp4)
            
        Returns:
            Path to the merged video file
        """
        # Validate input files exist
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Generate output path
        output_path = get_processed_video_path(output_video_id, output_format)
        
        try:
            # Create input streams
            video_input = ffmpeg.input(video_path, ss=video_start_time)
            audio_input = ffmpeg.input(audio_path, ss=audio_start_time)
            
            # Merge video and audio
            stream = ffmpeg.output(
                video_input,
                audio_input,
                output_path,
                vcodec='libx264',
                acodec='aac',
                **{
                    'b:v': '1000k',
                    'b:a': '128k',
                    'shortest': None  # End when shortest stream ends
                }
            )
            
            # Run the ffmpeg command
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error during audio-video merge: {e}")
    
    def replace_audio_in_video(
        self,
        video_path: str,
        audio_path: str,
        output_video_id: int,
        output_format: str = "mp4"
    ) -> str:
        """
        Replace the audio track in a video file
        
        Args:
            video_path: Path to video file
            audio_path: Path to new audio file
            output_video_id: ID for the output video file
            output_format: Output video format
            
        Returns:
            Path to the video with replaced audio
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        output_path = get_processed_video_path(output_video_id, output_format)
        
        try:
            video_input = ffmpeg.input(video_path)
            audio_input = ffmpeg.input(audio_path)
            
            # Remove original audio and add new audio
            stream = ffmpeg.output(
                video_input['v'],  # Video stream only
                audio_input['a'],  # Audio stream only
                output_path,
                vcodec='libx264',
                acodec='aac',
                **{
                    'b:v': '1000k',
                    'b:a': '128k',
                    'shortest': None
                }
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error during audio replacement: {e}")
    
    def add_background_music(
        self,
        video_path: str,
        music_path: str,
        output_video_id: int,
        music_volume: float = 0.3,
        original_volume: float = 1.0,
        output_format: str = "mp4"
    ) -> str:
        """
        Add background music to video while preserving original audio
        
        Args:
            video_path: Path to video file
            music_path: Path to background music file
            output_video_id: ID for the output video file
            music_volume: Volume level for background music (0.0-1.0)
            original_volume: Volume level for original audio (0.0-1.0)
            output_format: Output video format
            
        Returns:
            Path to the video with background music
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not os.path.exists(music_path):
            raise FileNotFoundError(f"Music file not found: {music_path}")
        
        output_path = get_processed_video_path(output_video_id, output_format)
        
        try:
            video_input = ffmpeg.input(video_path)
            music_input = ffmpeg.input(music_path)
            
            # Mix original audio with background music
            mixed_audio = ffmpeg.filter(
                [video_input['a'], music_input['a']],
                'amix',
                inputs=2,
                duration='first',
                weights=f'{original_volume} {music_volume}'
            )
            
            stream = ffmpeg.output(
                video_input['v'],
                mixed_audio,
                output_path,
                vcodec='libx264',
                acodec='aac',
                **{'b:v': '1000k', 'b:a': '128k'}
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error during background music addition: {e}")
    
    def extract_audio_from_video(
        self,
        video_path: str,
        output_audio_id: int,
        audio_format: str = "mp3"
    ) -> str:
        """
        Extract audio track from video file
        
        Args:
            video_path: Path to video file
            output_audio_id: ID for the output audio file
            audio_format: Audio format (mp3, wav, aac, etc.)
            
        Returns:
            Path to the extracted audio file
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        from config import get_audio_file_path
        output_path = get_audio_file_path(output_audio_id, audio_format)
        
        try:
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream['a'],
                output_path,
                acodec='libmp3lame' if audio_format.lower() == 'mp3' else 'aac',
                **{'b:a': '128k'}
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg error during audio extraction: {e}")

# Create global audio-video service instance
audio_video_service = AudioVideoService()