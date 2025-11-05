#!/usr/bin/env python3
"""
Launcher for GIF Background Remover GUI
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all dependencies are available"""
    try:
        import tkinter
        print("✅ Tkinter: Available")
    except ImportError:
        print("❌ Tkinter: Not available (usually comes with Python)")
        return False
    
    try:
        # Add the current directory to Python path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        from src.gif_processor import GIFProcessor
        from src.background_remover import BackgroundRemover
        print("✅ Core modules: Available")
        return True
    except ImportError as e:
        print(f"❌ Core modules: {e}")
        return False

def main():
    """Launch the GUI application"""
    print("🚀 Launching GIF Background Remover GUI...")
    
    if not check_dependencies():
        print("\n❌ Some dependencies are missing.")
        print("💡 Make sure you have:")
        print("   - Python with Tkinter support")
        print("   - All requirements installed: pip install -r requirements.txt")
        input("\nPress Enter to exit...")
        return
    
    try:
        from gui_app import main as gui_main
        print("✅ GUI loaded successfully!")
        print("🎨 Starting application...")
        gui_main()
    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()