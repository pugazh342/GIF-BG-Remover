"""
GIF Background Remover Tool
A powerful Python tool to remove backgrounds from GIF images
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .gif_processor import GIFProcessor
from .background_remover import BackgroundRemover
from .utils import setup_logging, validate_gif, create_output_path

__all__ = [
    'GIFProcessor', 
    'BackgroundRemover', 
    'setup_logging', 
    'validate_gif', 
    'create_output_path'
]