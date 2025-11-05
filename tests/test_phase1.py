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

class TestPhase1(unittest.TestCase):
    
    def setUp(self):
        self.processor = GIFProcessor()
        self.remover = BackgroundRemover()
        self.test_dir = Path(__file__).parent
        
    def create_test_gif(self, num_frames=3):
        """Create a simple test GIF for testing"""
        frames = []
        durations = []
        
        for i in range(num_frames):
            # Create simple colored frames
            img = Image.new('RGB', (50, 50), color=(i*80, 100, 150))
            frames.append(img)
            durations.append(100)  # 100ms per frame
        
        with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as f:
            output_path = f.name
        
        # Save the GIF
        frames[0].save(
            output_path,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0
        )
        return output_path
    
    def test_gif_info(self):
        """Test GIF information extraction"""
        gif_path = self.create_test_gif(num_frames=2)
        
        try:
            info = self.processor.get_gif_info(gif_path)
            self.assertEqual(info['frame_count'], 2)
            self.assertEqual(info['size'], (50, 50))
            self.assertTrue(info['is_animated'])
        finally:
            if os.path.exists(gif_path):
                os.unlink(gif_path)
    
    def test_frame_extraction(self):
        """Test frame extraction from GIF"""
        gif_path = self.create_test_gif(num_frames=3)
        
        try:
            frames, durations = self.processor.extract_frames(gif_path)
            self.assertEqual(len(frames), 3)
            self.assertEqual(len(durations), 3)
            
            # Check frame properties
            for frame in frames:
                self.assertEqual(frame.mode, 'RGBA')  # Should be converted to RGBA
                self.assertEqual(frame.size, (50, 50))
                
        finally:
            if os.path.exists(gif_path):
                os.unlink(gif_path)
    
    def test_background_remover_placeholder(self):
        """Test that background remover processes frames (placeholder)"""
        test_image = Image.new('RGBA', (50, 50), color=(255, 0, 0, 255))
        processed = self.remover.process_frame(test_image)
        
        self.assertEqual(processed.mode, 'RGBA')
        self.assertEqual(processed.size, (50, 50))

if __name__ == '__main__':
    unittest.main()