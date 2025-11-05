#!/usr/bin/env python3
"""
GIF Background Remover Tool
Complete Version with CLI and GUI Support

Phases:
- Phase 1: Basic GIF Frame Processing
- Phase 2: Background Removal Algorithms  
- Phase 3: AI-Powered Removal
- Phase 4: GUI Support
"""

import os
import sys
from pathlib import Path
import argparse
import logging

# Check if GUI is requested
if len(sys.argv) == 1 or '--gui' in sys.argv or '-g' in sys.argv:
    try:
        from gui_app import main as gui_main
        print("🚀 Launching GIF Background Remover GUI...")
        gui_main()
        sys.exit(0)
    except ImportError as e:
        print(f"❌ GUI not available: {e}")
        print("💡 Falling back to CLI version...")
        # Remove GUI arguments and continue with CLI
        sys.argv = [arg for arg in sys.argv if arg not in ['--gui', '-g']]

# Add the current directory to Python path for package imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from src.gif_processor import GIFProcessor
    from src.background_remover import BackgroundRemover
    from src.utils import create_output_path
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("💡 Make sure all modules are available:")
    print("   - gif_bg_remover/gif_processor.py")
    print("   - gif_bg_remover/background_remover.py") 
    print("   - gif_bg_remover/utils.py")
    print("\n📦 Install dependencies: pip install -r requirements.txt")
    sys.exit(1)

def print_banner():
    """Print the tool banner"""
    print("🎉 GIF Background Remover Tool")
    print("🚀 Complete Version with AI-Powered Background Removal")
    print("=" * 60)

def check_dependencies():
    """Check if required dependencies are available"""
    print("\n📦 Dependency Check:")
    
    dependencies = {
        "Pillow (Image Processing)": "PIL",
        "OpenCV (Computer Vision)": "cv2",
        "NumPy (Array Operations)": "numpy", 
        "scikit-image (Advanced Processing)": "skimage",
        "PyTest (Testing)": "pytest"
    }
    
    ai_available = False
    try:
        from rembg import remove
        ai_available = True
        print("✅ AI Background Removal: Available (rembg)")
    except ImportError:
        print("❌ AI Background Removal: Not available (install with: pip install rembg)")
    except Exception as e:
        print(f"❌ AI Background Removal: Installed but has issues - {e}")
    
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {name}: Available")
        except ImportError:
            print(f"❌ {name}: Not available")
    
    return ai_available

def print_method_info(method):
    """Print information about each background removal method"""
    methods = {
        "auto": "🤖 Auto - Smart detection (AI → Color → Edges)",
        "ai": "🧠 AI - Best for complex images, people, objects",
        "color": "🎨 Color - Remove specific background colors", 
        "edges": "✂️ Edges - Detect and keep foreground objects"
    }
    
    print(f"\n🎯 Selected Method: {methods.get(method, method)}")
    
    if method == "color":
        print("💡 Tip: Use --color R G B to specify background color")
        print("   Example: --color 255 255 255 for white background")
    elif method == "edges":
        print("💡 Tip: Best for images with clear foreground/background separation")
    elif method == "ai":
        print("💡 Tip: Best for complex images, portraits, animals")
        print("   Note: First run may download AI model (~176MB)")

def main():
    parser = argparse.ArgumentParser(
        description='GIF Background Remover - Remove backgrounds from GIFs using multiple methods',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
Examples:
  {sys.argv[0]} input.gif                    # Auto-detect best method
  {sys.argv[0]} input.gif --method ai        # Use AI-powered removal
  {sys.argv[0]} input.gif --method color --color 255 255 255  # Remove white background
  {sys.argv[0]} input.gif --method edges     # Use edge detection
  {sys.argv[0]} input.gif --info             # Show GIF information
  {sys.argv[0]} input.gif --preview          # Preview frame extraction
  {sys.argv[0]} --gui                        # Launch graphical interface
  {sys.argv[0]} --check-deps                 # Check dependencies

Background Removal Methods:
  auto    - Automatically choose best method (AI → Color → Edges)
  ai      - AI-powered removal (best for complex images)
  color   - Remove specific color (use with --color)
  edges   - Edge detection based removal

Output Quality:
  Higher quality methods may take longer but produce better results
  AI > Color > Edges (in most cases)
        '''
    )
    
    # Required arguments
    parser.add_argument('input', nargs='?', help='Input GIF file path')
    
    # Output options
    parser.add_argument('-o', '--output', help='Output GIF file path')
    parser.add_argument('--suffix', default='_nobg', help='Suffix for output file (default: _nobg)')
    parser.add_argument('--quality', type=int, choices=[1, 2, 3], default=2,
                       help='Output quality: 1=Fast, 2=Balanced, 3=Best (default: 2)')
    
    # Background removal options
    parser.add_argument('--method', 
                       choices=['color', 'edges', 'ai', 'auto'], 
                       default='auto',
                       help='Background removal method (default: auto)')
    
    # Color-based removal options
    parser.add_argument('--color', nargs=3, type=int, metavar=('R', 'G', 'B'),
                       help='Target background color (e.g., 255 255 255 for white)')
    parser.add_argument('--tolerance', type=int, default=40,
                       help='Color tolerance for color-based removal (0-255, default: 40)')
    
    # Edge-based removal options
    parser.add_argument('--blur-kernel', type=int, default=5,
                       help='Blur kernel size for edge detection (default: 5)')
    parser.add_argument('--canny-low', type=int, default=50,
                       help='Canny edge detection lower threshold (default: 50)')
    parser.add_argument('--canny-high', type=int, default=150,
                       help='Canny edge detection higher threshold (default: 150)')
    
    # Information and debugging
    parser.add_argument('--info', action='store_true', help='Show GIF information only')
    parser.add_argument('--preview', action='store_true', help='Preview frame extraction')
    parser.add_argument('--check-deps', action='store_true', help='Check dependencies and exit')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('-g', '--gui', action='store_true', help='Launch graphical user interface')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check dependencies if requested
    if args.check_deps:
        check_dependencies()
        return
    
    # If no input provided and not GUI, show help
    if not args.input and not args.gui:
        parser.print_help()
        print(f"\n💡 Quick Start:")
        print(f"  1. Create test images: python create_test_images.py")
        print(f"  2. Test basic functionality: python main.py sample.gif --info")
        print(f"  3. Try AI removal: python main.py sample.gif --method ai")
        print(f"  4. Launch GUI: python main.py --gui")
        print(f"  5. Check dependencies: python main.py --check-deps")
        return
    
    # Validate input file exists (if provided)
    if args.input and not Path(args.input).exists():
        print(f"❌ Error: Input file '{args.input}' not found")
        print(f"💡 Current directory: {os.getcwd()}")
        sys.exit(1)
    
    # Setup processors
    log_level = logging.DEBUG if args.verbose else logging.INFO
    processor = GIFProcessor(log_level=log_level)
    remover = BackgroundRemover(log_level=log_level)
    
    try:
        if args.info or args.preview:
            # Show GIF information
            info = processor.get_gif_info(args.input)
            print(f"\n📊 GIF Information:")
            print(f"  File: {args.input}")
            print(f"  Frames: {info['frame_count']}")
            print(f"  Size: {info['size']}")
            print(f"  Mode: {info['mode']}")
            print(f"  Animated: {info['is_animated']}")
            print(f"  Duration: {info['duration']:.2f} seconds")
            
            if args.preview:
                print(f"\n🔍 Frame Preview:")
                processor.preview_frames(args.input)
        
        else:
            # Process the GIF with background removal
            output_path = args.output or create_output_path(args.input, args.suffix)
            
            print(f"\n🔄 Processing GIF:")
            print(f"  Input: {args.input}")
            print(f"  Output: {output_path}")
            print(f"  Quality: {['Fast', 'Balanced', 'Best'][args.quality-1]}")
            
            # Print method information
            print_method_info(args.method)
            
            # Prepare kwargs for background removal
            kwargs = {}
            if args.method == 'color':
                if args.color:
                    kwargs['target_color'] = tuple(args.color)
                else:
                    kwargs['target_color'] = (255, 255, 255)  # Default to white
                kwargs['tolerance'] = args.tolerance
                print(f"  Target color: {kwargs['target_color']}")
                print(f"  Tolerance: {args.tolerance}")
            
            elif args.method == 'edges':
                kwargs['blur_kernel'] = args.blur_kernel
                kwargs['canny_low'] = args.canny_low
                kwargs['canny_high'] = args.canny_high
                print(f"  Blur kernel: {args.blur_kernel}")
                print(f"  Canny thresholds: {args.canny_low}-{args.canny_high}")
            
            elif args.method == 'ai':
                ai_available = check_dependencies()
                if not ai_available:
                    print("⚠️  AI method selected but rembg not available.")
                    print("💡 Falling back to auto mode...")
                    args.method = 'auto'
            
            elif args.method == 'auto':
                print(f"  Auto-selecting best removal method...")
            
            # Extract frames
            print(f"\n📂 Extracting frames...")
            frames, durations = processor.extract_frames(args.input)
            print(f"✅ Extracted {len(frames)} frames")
            
            # Adjust processing based on quality setting
            if args.quality == 1 and len(frames) > 10:
                # Fast mode: process every other frame for long GIFs
                print("⚡ Fast mode: Processing key frames only")
                frames = frames[::2]
                durations = durations[::2]
            
            # Process frames with background removal
            print(f"\n🎨 Removing backgrounds...")
            processed_frames = []
            
            for i, frame in enumerate(frames):
                processed_frame = remover.process_frame(frame, method=args.method, **kwargs)
                processed_frames.append(processed_frame)
                
                # Progress indicator
                progress = (i + 1) / len(frames) * 100
                if args.verbose or i % 5 == 0 or i == len(frames) - 1:
                    print(f"  🖼️  Processed frame {i+1}/{len(frames)} ({progress:.1f}%)")
                else:
                    print(f"  🖼️  Processed frame {i+1}/{len(frames)} ({progress:.1f}%)", end='\r')
            
            print(f"\n✅ Background removal completed")
            
            # Create output GIF
            print(f"\n💾 Saving output GIF...")
            optimize = args.quality >= 2  # Optimize for balanced and best quality
            processor.create_gif(processed_frames, durations, output_path, optimize=optimize)
            
            # Show results
            print(f"\n🎉 Processing Complete!")
            print(f"  ✅ Original: {args.input}")
            print(f"  ✅ Processed: {output_path}")
            print(f"  📊 Frames processed: {len(frames)}")
            print(f"  ⏱️  Total duration: {sum(durations)/1000:.2f}s")
            
            # Show file sizes
            input_size = Path(args.input).stat().st_size / 1024
            output_size = Path(output_path).stat().st_size / 1024
            size_change = ((output_size - input_size) / input_size) * 100
            print(f"  📦 File size: {input_size:.1f}KB → {output_size:.1f}KB ({size_change:+.1f}%)")
            
            # Quality assessment
            if size_change > 50:
                print("  💡 Large size increase: Consider using lower quality setting")
            elif size_change < -20:
                print("  💡 Good compression: Background removal effective")
            
            print(f"\n🎯 Next Steps:")
            print(f"  1. Open the output file to check results")
            print(f"  2. Try different methods if not satisfied")
            print(f"  3. Use --quality 1 for faster processing")
            print(f"  4. Use GUI for easier file selection: python main.py --gui")
    
    except KeyboardInterrupt:
        print(f"\n❌ Processing interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        
        print(f"\n🔧 Troubleshooting:")
        print(f"  • Check if input file is a valid GIF")
        print(f"  • Try with --method color for solid backgrounds") 
        print(f"  • Use --verbose for detailed error information")
        print(f"  • Ensure all dependencies are installed")
        
        sys.exit(1)

if __name__ == "__main__":
    main()