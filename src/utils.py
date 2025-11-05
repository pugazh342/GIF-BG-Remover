import logging
from pathlib import Path

def setup_logging(name=None, level=logging.INFO):
    """Setup basic logging configuration"""
    logging.basicConfig(
        level=level,  # Use the level parameter, not the name
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(name)  # Use name for the logger, not for level

def validate_gif(file_path):
    """
    Validate if file exists and is a GIF
    Returns: (is_valid, error_message)
    """
    path = Path(file_path)
    
    if not path.exists():
        return False, f"File not found: {file_path}"
    
    if path.suffix.lower() not in ['.gif']:
        return False, f"Not a GIF file: {file_path}"
    
    return True, "Valid GIF file"

def create_output_path(input_path, suffix="_nobg"):
    """
    Create output path by adding suffix to filename
    """
    input_path = Path(input_path)
    output_path = input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}"
    return output_path