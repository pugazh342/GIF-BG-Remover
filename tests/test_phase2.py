import unittest
from pathlib import Path
import tempfile
import sys
import os

# Add the parent directory to Python path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gif_processor import GIFProcessor
from src.background_remover import BackgroundRemover
from PIL import Image
import numpy as np

class TestPhase2(unittest.TestCase):
    
    def setUp(self):
        self.processor = GIFProcessor()
        self.remover = BackgroundRemover()
    
    def create_test_image_with_background(self, bg_color, fg_color, shape='circle'):
        """Create a test image with specific background and foreground"""
        img = Image.new('RGB', (50, 50), color=bg_color)
        
        if shape == 'circle':
            # Draw a circle
            for x in range(50):
                for y in range(50):
                    if (x-25)**2 + (y-25)**2 < 100:  # Circle
                        img.putpixel((x, y), fg_color)
        elif shape == 'square':
            # Draw a square
            for x in range(15, 35):
                for y in range(15, 35):
                    img.putpixel((x, y), fg_color)
        
        return img.convert('RGBA')
    
    def test_color_based_removal(self):
        """Test color-based background removal"""
        # Create image with white background and red circle
        test_img = self.create_test_image_with_background(
            bg_color=(255, 255, 255),  # White background
            fg_color=(255, 0, 0),      # Red circle
            shape='circle'
        )
        
        # Remove white background
        result = self.remover.remove_background_color_based(
            test_img, 
            target_color=(255, 255, 255),
            tolerance=40
        )
        
        # Convert to array for analysis
        result_array = np.array(result)
        
        # Check that background areas are transparent
        # Top-left corner should be background (transparent)
        self.assertEqual(result_array[0, 0, 3], 0)  # Alpha should be 0 (transparent)
        
        # Center should be foreground (opaque)
        self.assertEqual(result_array[25, 25, 3], 255)  # Alpha should be 255 (opaque)
    
    def test_edge_based_removal(self):
        """Test edge-based background removal"""
        # Create image with distinct shapes
        test_img = self.create_test_image_with_background(
            bg_color=(0, 0, 0),        # Black background
            fg_color=(0, 255, 0),      # Green square
            shape='square'
        )
        
        # Remove background using edges
        result = self.remover.remove_background_edges(test_img)
        
        # Convert to array for analysis
        result_array = np.array(result)
        
        # The result should have some transparency
        alpha_channel = result_array[:, :, 3]
        self.assertTrue(np.any(alpha_channel == 0))  # Some transparent pixels
        self.assertTrue(np.any(alpha_channel == 255))  # Some opaque pixels
    
    def test_adaptive_removal(self):
        """Test adaptive background removal"""
        test_img = self.create_test_image_with_background(
            bg_color=(255, 255, 255),
            fg_color=(0, 0, 255),
            shape='circle'
        )
        
        # Test color method
        result_color = self.remover.remove_background_adaptive(test_img, method='color')
        
        # Test edges method
        result_edges = self.remover.remove_background_adaptive(test_img, method='edges')
        
        # Both should return images
        self.assertEqual(result_color.size, (50, 50))
        self.assertEqual(result_edges.size, (50, 50))
        self.assertEqual(result_color.mode, 'RGBA')
        self.assertEqual(result_edges.mode, 'RGBA')

if __name__ == '__main__':
    unittest.main()