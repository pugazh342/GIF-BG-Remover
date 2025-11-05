#!/usr/bin/env python3
"""
Test script to verify rembg installation
"""

try:
    print("Testing rembg import...")
    from rembg import remove
    print("✅ rembg import successful!")
    
    print("Testing rembg function...")
    from PIL import Image
    import io
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    
    # Test the remove function
    result = remove(img)
    print("✅ rembg remove function works!")
    print(f"Result image mode: {result.mode}")
    print(f"Result image size: {result.size}")
    
except ImportError as e:
    print(f"❌ rembg import failed: {e}")
except Exception as e:
    print(f"❌ rembg test failed: {e}")