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

class TestPhase3(unittest.TestCase):
    
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
    
    def test_ai_method_availability(self):
        """Test that AI method is available or gracefully handled"""
        test_img = self.create_test_image_with_background(
            bg_color=(255, 255, 255),
            fg_color=(255, 0, 0),
            shape='circle'
        )
        
        # This should work regardless of AI availability
        result = self.remover.process_frame(test_img, method='ai')
        
        # Should return an image
        self.assertEqual(result.mode, 'RGBA')
        self.assertEqual(result.size, (50, 50))
    
    def test_auto_method_with_ai(self):
        """Test auto method that prefers AI"""
        test_img = self.create_test_image_with_background(
            bg_color=(255, 255, 255),
            fg_color=(0, 255, 0),
            shape='square'
        )
        
        result = self.remover.process_frame(test_img, method='auto')
        
        # Should return a processed image
        self.assertEqual(result.mode, 'RGBA')
        self.assertEqual(result.size, (50, 50))
    
    def test_all_methods_available(self):
        """Test that all methods return valid images"""
        test_img = self.create_test_image_with_background(
            bg_color=(200, 200, 200),
            fg_color=(100, 100, 255),
            shape='circle'
        )
        
        methods = ['color', 'edges', 'ai', 'auto']
        
        for method in methods:
            with self.subTest(method=method):
                result = self.remover.process_frame(test_img, method=method)
                self.assertEqual(result.mode, 'RGBA')
                self.assertEqual(result.size, (50, 50))

if __name__ == '__main__':
    unittest.main()