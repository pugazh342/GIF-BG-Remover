import os
from PIL import Image, ImageSequence
import numpy as np
from pathlib import Path
import logging
from typing import List, Tuple, Optional

# Remove relative imports, use direct imports
try:
    from utils import validate_gif, setup_logging
except ImportError:
    # Fallback for when running as main
    from .utils import validate_gif, setup_logging

class GIFProcessor:
    """
    Handles GIF frame extraction and reconstruction
    """
    
    def __init__(self, log_level=logging.INFO):
        self.logger = setup_logging('GIFProcessor', log_level)  # Fixed: pass name and level separately
    
    def extract_frames(self, gif_path: str) -> Tuple[List[Image.Image], List[int]]:
        """
        Extract all frames from GIF with their durations
        
        Returns:
            Tuple of (frames, durations)
        """
        is_valid, error_msg = validate_gif(gif_path)
        if not is_valid:
            raise ValueError(error_msg)
        
        try:
            with Image.open(gif_path) as gif:
                frames = []
                durations = []
                
                for frame in ImageSequence.Iterator(gif):
                    # Convert to RGBA to ensure transparency support
                    rgba_frame = frame.convert('RGBA')
                    frames.append(rgba_frame)
                    
                    # Get frame duration (default to 100ms if not specified)
                    duration = frame.info.get('duration', 100)
                    durations.append(duration)
                
                self.logger.info(f"✅ Extracted {len(frames)} frames from {gif_path}")
                return frames, durations
                
        except Exception as e:
            self.logger.error(f"❌ Failed to extract frames from {gif_path}: {str(e)}")
            raise
    
    def create_gif(self, 
                   frames: List[Image.Image], 
                   durations: List[int], 
                   output_path: str,
                   optimize: bool = True,
                   loop: int = 0) -> None:
        """
        Create a GIF from processed frames
        
        Args:
            frames: List of PIL Image objects
            durations: List of frame durations in milliseconds
            output_path: Output file path
            optimize: Whether to optimize the GIF
            loop: Number of loops (0 = infinite)
        """
        try:
            if not frames:
                raise ValueError("No frames provided to create GIF")
            
            if len(frames) != len(durations):
                raise ValueError("Frames and durations lists must have same length")
            
            # Save first frame and append subsequent frames
            first_frame = frames[0]
            remaining_frames = frames[1:]
            
            first_frame.save(
                output_path,
                format='GIF',
                save_all=True,
                append_images=remaining_frames,
                duration=durations,
                loop=loop,
                optimize=optimize,
                transparency=0, # Set transparency index
                disposal=2
            )
            
            self.logger.info(f"✅ Created GIF with {len(frames)} frames: {output_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create GIF {output_path}: {str(e)}")
            raise
    
    def get_gif_info(self, gif_path: str) -> dict:
        """
        Get basic information about GIF file
        """
        try:
            with Image.open(gif_path) as gif:
                frames = list(ImageSequence.Iterator(gif))
                info = {
                    'frame_count': len(frames),
                    'size': gif.size,
                    'mode': gif.mode,
                    'is_animated': getattr(gif, 'is_animated', False),
                    'duration': sum(frame.info.get('duration', 100) for frame in frames) / 1000.0
                }
                return info
        except Exception as e:
            self.logger.error(f"❌ Failed to get GIF info for {gif_path}: {str(e)}")
            raise
    
    def preview_frames(self, gif_path: str, max_frames: int = 5) -> None:
        """
        Preview first few frames of GIF (for debugging)
        """
        info = self.get_gif_info(gif_path)
        print(f"📊 GIF Info: {gif_path}")
        print(f"  - Frames: {info['frame_count']}")
        print(f"  - Size: {info['size']}")
        print(f"  - Mode: {info['mode']}")
        print(f"  - Animated: {info['is_animated']}")
        print(f"  - Total Duration: {info['duration']:.2f}s")
        
        frames, durations = self.extract_frames(gif_path)
        print(f"  - First {min(max_frames, len(frames))} frame durations: {durations[:max_frames]} ms")