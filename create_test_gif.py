from PIL import Image

# Create a simple test GIF
frames = []
durations = []

# Create 3 different colored frames
for i in range(3):
    img = Image.new('RGB', (100, 100), color=(i*80, 100, 150))
    frames.append(img)
    durations.append(500)  # 500ms per frame

# Save as GIF
frames[0].save(
    'sample.gif',
    format='GIF',
    save_all=True,
    append_images=frames[1:],
    duration=durations,
    loop=0
)

print("✅ Created sample.gif for testing")