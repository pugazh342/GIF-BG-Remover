from PIL import Image
import os

def create_test_images():
    """Create test images with different backgrounds"""
    
    # Create test directory
    test_dir = "test_images"
    os.makedirs(test_dir, exist_ok=True)
    
    # 1. White background with colored circle
    img1 = Image.new('RGB', (100, 100), color='white')
    for x in range(100):
        for y in range(100):
            if (x-50)**2 + (y-50)**2 < 400:  # Circle
                img1.putpixel((x, y), (255, 0, 0))  # Red circle
    img1.save(f'{test_dir}/white_bg_red_circle.gif')
    
    # 2. Black background with colored square
    img2 = Image.new('RGB', (100, 100), color='black')
    for x in range(30, 70):
        for y in range(30, 70):
            img2.putpixel((x, y), (0, 255, 0))  # Green square
    img2.save(f'{test_dir}/black_bg_green_square.gif')
    
    # 3. Blue background with yellow triangle
    img3 = Image.new('RGB', (100, 100), color=(0, 0, 255))
    for x in range(100):
        for y in range(100):
            if x > y and x < 100 - y:  # Triangle
                img3.putpixel((x, y), (255, 255, 0))  # Yellow triangle
    img3.save(f'{test_dir}/blue_bg_yellow_triangle.gif')
    
    print("✅ Created test images:")
    print(f"   - {test_dir}/white_bg_red_circle.gif")
    print(f"   - {test_dir}/black_bg_green_square.gif") 
    print(f"   - {test_dir}/blue_bg_yellow_triangle.gif")
    print("\n🎯 Test commands:")
    print("   python main.py test_images/white_bg_red_circle.gif --method color --color 255 255 255")
    print("   python main.py test_images/black_bg_green_square.gif --method color --color 0 0 0")
    print("   python main.py test_images/blue_bg_yellow_triangle.gif --method edges")

if __name__ == "__main__":
    create_test_images()