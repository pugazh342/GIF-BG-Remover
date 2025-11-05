import numpy as np
from PIL import Image
import logging
from typing import Tuple, List, Optional
import cv2
import os

# Remove relative imports, use direct imports
try:
    from utils import setup_logging
except ImportError:
    # Fallback for when running as main
    from .utils import setup_logging

class BackgroundRemover:
    """
    Advanced background removal with multiple methods including AI
    """
    
    def __init__(self, log_level=logging.INFO):
        self.logger = setup_logging('BackgroundRemover', log_level)
        self.ai_model = None
    
    def _load_ai_model(self):
        """Lazy loading of AI model"""
        if self.ai_model is None:
            try:
                from rembg import remove as rembg_remove
                self.ai_model = rembg_remove
                self.logger.info("✅ AI model loaded successfully")
            except ImportError:
                self.logger.warning("❌ Rembg not available. Install with: pip install rembg")
                self.ai_model = None
        return self.ai_model
    
    def pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """Convert PIL Image to OpenCV format (BGR)"""
        # Convert PIL RGB to OpenCV BGR
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        return cv_image
    
    def cv2_to_pil(self, cv2_image: np.ndarray) -> Image.Image:
        """Convert OpenCV image (BGR) to PIL format (RGB)"""
        # Convert OpenCV BGR to PIL RGB
        rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_image)
    
    def remove_background_ai(self, image: Image.Image) -> Image.Image:
        """
        Remove background using AI model (rembg)
        
        Args:
            image: PIL Image
        
        Returns:
            Image with transparent background
        """
        ai_remove = self._load_ai_model()
        if ai_remove is None:
            self.logger.warning("AI model not available, falling back to edge detection")
            return self.remove_background_edges(image)
        
        try:
            # Convert to RGB if needed (rembg expects RGB)
            if image.mode != 'RGB':
                image_rgb = image.convert('RGB')
            else:
                image_rgb = image
            
            # Use AI to remove background
            result = ai_remove(image_rgb)
            
            # Ensure result is RGBA
            if result.mode != 'RGBA':
                result = result.convert('RGBA')
                
            self.logger.info("✅ AI background removal completed")
            return result
            
        except Exception as e:
            self.logger.error(f"AI background removal failed: {e}")
            self.logger.warning("Falling back to edge detection")
            return self.remove_background_edges(image)
    
    def remove_background_color_based(self, image: Image.Image, target_color: Tuple[int, int, int], 
                                    tolerance: int = 40) -> Image.Image:
        """
        Remove background based on color similarity
        
        Args:
            image: PIL Image in RGBA format
            target_color: RGB color to remove (e.g., (255, 255, 255) for white)
            tolerance: Color similarity tolerance (0-255)
        
        Returns:
            Image with transparent background where target color was found
        """
        # Convert to numpy array
        img_array = np.array(image)
        
        # Create mask for pixels similar to target color
        r, g, b = target_color
        lower_bound = np.array([max(0, r - tolerance), 
                              max(0, g - tolerance), 
                              max(0, b - tolerance), 0])
        upper_bound = np.array([min(255, r + tolerance), 
                              min(255, g + tolerance), 
                              min(255, b + tolerance), 255])
        
        # Create mask
        mask = cv2.inRange(img_array, lower_bound, upper_bound)
        
        # Invert mask (we want to keep non-background areas)
        mask = cv2.bitwise_not(mask)
        
        # Apply mask to alpha channel
        result = img_array.copy()
        result[:, :, 3] = cv2.bitwise_and(result[:, :, 3], mask)
        
        return Image.fromarray(result)
    
    def remove_background_edges(self, image: Image.Image, 
                              blur_kernel: int = 5, 
                              canny_low: int = 50, 
                              canny_high: int = 150) -> Image.Image:
        """
        Remove background using edge detection and contour filling
        
        Args:
            image: PIL Image in RGBA format
            blur_kernel: Gaussian blur kernel size
            canny_low: Canny edge detection lower threshold
            canny_high: Canny edge detection higher threshold
        
        Returns:
            Image with transparent background
        """
        try:
            # Convert to OpenCV format (BGR)
            cv_image = self.pil_to_cv2(image)
            
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, canny_low, canny_high)
            
            # Dilate edges to close gaps
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Create mask
            mask = np.zeros_like(gray)
            if contours:
                cv2.fillPoly(mask, contours, 255)
            
            # Convert back to PIL and apply mask to alpha channel
            result_pil = image.copy()
            result_array = np.array(result_pil)
            result_array[:, :, 3] = mask  # Apply mask to alpha channel
            
            return Image.fromarray(result_array)
            
        except Exception as e:
            self.logger.error(f"Edge-based removal failed: {e}")
            return image  # Return original if edge detection fails
    
    def remove_background_adaptive(self, image: Image.Image, 
                                 method: str = "auto", 
                                 **kwargs) -> Image.Image:
        """
        Adaptive background removal with multiple methods
        
        Args:
            image: PIL Image in RGBA format
            method: Removal method ("color", "edges", "ai", "auto")
            **kwargs: Additional parameters for specific methods
        
        Returns:
            Image with transparent background
        """
        self.logger.info(f"Using {method} method for background removal")
        
        if method == "color":
            target_color = kwargs.get('target_color', (255, 255, 255))  # Default: white
            tolerance = kwargs.get('tolerance', 40)
            return self.remove_background_color_based(image, target_color, tolerance)
        
        elif method == "edges":
            blur_kernel = kwargs.get('blur_kernel', 5)
            canny_low = kwargs.get('canny_low', 50)
            canny_high = kwargs.get('canny_high', 150)
            return self.remove_background_edges(image, blur_kernel, canny_low, canny_high)
        
        elif method == "ai":
            return self.remove_background_ai(image)
        
        elif method == "auto":
            # Try AI first if available
            ai_remove = self._load_ai_model()
            if ai_remove is not None:
                self.logger.info("Auto: Trying AI method first")
                try:
                    result = self.remove_background_ai(image)
                    # Check if AI produced good results
                    alpha_channel = np.array(result)[:, :, 3]
                    transparent_pixels = np.sum(alpha_channel == 0)
                    total_pixels = alpha_channel.size
                    
                    if transparent_pixels / total_pixels > 0.1:  # If we have significant transparency
                        self.logger.info("Auto: AI method produced good results")
                        return result
                except Exception as e:
                    self.logger.warning(f"Auto: AI method failed: {e}")
            
            # Fall back to color-based for solid backgrounds
            self.logger.info("Auto: Trying color-based method")
            try:
                result = self.remove_background_color_based(image, (255, 255, 255), 40)
                alpha_channel = np.array(result)[:, :, 3]
                if np.mean(alpha_channel) > 10:  # If we have some transparency
                    self.logger.info("Auto: Color-based method produced good results")
                    return result
            except Exception as e:
                self.logger.warning(f"Auto: Color-based method failed: {e}")
            
            # Final fallback to edge-based
            self.logger.info("Auto: Using edge-based method as fallback")
            return self.remove_background_edges(image)
        
        else:
            self.logger.warning(f"Unknown method: {method}. Returning original image.")
            return image
    
    def process_frame(self, frame: Image.Image, method: str = "auto", **kwargs) -> Image.Image:
        """
        Process a single frame for background removal
        
        Args:
            frame: PIL Image frame
            method: Background removal method
            **kwargs: Additional parameters for the removal method
        
        Returns:
            Processed frame with transparent background
        """
        try:
            return self.remove_background_adaptive(frame, method, **kwargs)
        except Exception as e:
            self.logger.error(f"Background removal failed: {e}")
            return frame  # Return original frame if removal fails