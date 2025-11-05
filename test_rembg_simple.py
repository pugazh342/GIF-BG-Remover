#!/usr/bin/env python3
"""
Simple test for rembg
"""
try:
    print("Testing rembg...")
    from rembg import remove
    from PIL import Image
    print("✅ rembg imported successfully!")
    
    # Test with a simple image
    img = Image.new('RGB', (100, 100), color='red')
    result = remove(img)
    print(f"✅ rembg works! Output: {result.mode}, {result.size}")
    
except Exception as e:
    print(f"❌ rembg failed: {e}")
    print("Trying alternative installation...")