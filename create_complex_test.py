from PIL import Image, ImageDraw
import os

def create_complex_test_images():
    """Create more complex test images for AI testing"""
    
    # Create test directory
    test_dir = "test_images_complex"
    os.makedirs(test_dir, exist_ok=True)
    
    # 1. Person silhouette (simulated)
    img1 = Image.new('RGB', (200, 300), color='lightblue')
    draw = ImageDraw.Draw(img1)  # Fixed: ImageDraw.Draw
    # Draw a simple person shape
    draw.ellipse((75, 50, 125, 100), fill='red')  # Head
    draw.rectangle((90, 100, 110, 200), fill='red')  # Body
    draw.rectangle((60, 120, 90, 160), fill='red')  # Left arm
    draw.rectangle((110, 120, 140, 160), fill='red')  # Right arm
    draw.rectangle((80, 200, 100, 250), fill='red')  # Left leg
    draw.rectangle((100, 200, 120, 250), fill='red')  # Right leg
    img1.save(f'{test_dir}/person_silhouette.gif')
    
    # 2. Object with complex background
    img2 = Image.new('RGB', (150, 150), color='green')
    draw = ImageDraw.Draw(img2)  # Fixed: ImageDraw.Draw
    # Draw multiple overlapping shapes
    draw.ellipse((20, 20, 80, 80), fill='yellow')
    draw.rectangle((60, 60, 120, 120), fill='blue')
    draw.polygon([(100, 30), (130, 80), (70, 100)], fill='red')
    img2.save(f'{test_dir}/complex_shapes.gif')
    
    # 3. Gradient background
    img3 = Image.new('RGB', (180, 180))
    for x in range(180):
        for y in range(180):
            # Create a gradient from white to blue
            r = 255 - int(x * 255 / 180)
            g = 255 - int(y * 255 / 180)
            b = 255
            img3.putpixel((x, y), (r, g, b))
    # Add a foreground object
    draw = ImageDraw.Draw(img3)  # Fixed: ImageDraw.Draw
    draw.rectangle((60, 60, 120, 120), fill='orange')
    img3.save(f'{test_dir}/gradient_background.gif')
    
    print("✅ Created complex test images:")
    print(f"   - {test_dir}/person_silhouette.gif")
    print(f"   - {test_dir}/complex_shapes.gif")
    print(f"   - {test_dir}/gradient_background.gif")
    print("\n🎯 Test AI commands:")
    print("   python main.py test_images_complex/person_silhouette.gif --method ai")
    print("   python main.py test_images_complex/complex_shapes.gif --method ai")
    print("   python main.py test_images_complex/gradient_background.gif --method auto")

if __name__ == "__main__":
    create_complex_test_images()