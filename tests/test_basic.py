import unittest
from pathlib import Path
import os
from src.utils import validate_gif, create_output_path

class TestBasicFunctions(unittest.TestCase):
    
    def test_validate_gif_nonexistent(self):
        is_valid, message = validate_gif("nonexistent.gif")
        self.assertFalse(is_valid)
        self.assertIn("not found", message)
    
    def test_create_output_path(self):
        input_path = "test/test.gif"
        output_path = create_output_path(input_path)
        expected = Path("test/test_nobg.gif")
        # Use Path objects for cross-platform comparison
        self.assertEqual(output_path, expected)
    
    def test_create_output_path_with_custom_suffix(self):
        input_path = "image.gif"
        output_path = create_output_path(input_path, "_transparent")
        expected = Path("image_transparent.gif")
        self.assertEqual(output_path, expected)

if __name__ == '__main__':
    unittest.main()