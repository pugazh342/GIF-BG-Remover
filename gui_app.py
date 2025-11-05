#!/usr/bin/env python3
"""
GIF Background Remover - GUI Application
Phase 4: Graphical User Interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import sys
import os
import threading

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from src.gif_processor import GIFProcessor
    from src.background_remover import BackgroundRemover
    from src.utils import create_output_path
except ImportError as e:
    print(f"Import Error: {e}")
    print("Make sure all modules are available")

class GIFBackgroundRemoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GIF Background Remover 🎨")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Initialize processors
        self.processor = GIFProcessor()
        self.remover = BackgroundRemover()
        
        # Variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.method_var = tk.StringVar(value="auto")
        self.target_color = tk.StringVar(value="255,255,255")
        self.tolerance_var = tk.IntVar(value=40)
        self.is_processing = False
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="🎉 GIF Background Remover", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input File Section
        input_frame = ttk.LabelFrame(main_frame, text="Input GIF", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="Select GIF File:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.input_path).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(input_frame, text="Browse", command=self.browse_input).grid(row=0, column=2)
        ttk.Button(input_frame, text="Get Info", command=self.get_gif_info).grid(row=0, column=3, padx=(5, 0))
        
        # Output File Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Settings", padding="10")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(output_frame, textvariable=self.output_path).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=2)
        
        # Method Selection
        method_frame = ttk.LabelFrame(main_frame, text="Background Removal Method", padding="10")
        method_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        methods = [
            ("Auto (Smart Detection)", "auto"),
            ("AI-Powered (Best Quality)", "ai"),
            ("Color-Based", "color"),
            ("Edge Detection", "edges")
        ]
        
        for i, (text, value) in enumerate(methods):
            ttk.Radiobutton(method_frame, text=text, variable=self.method_var, 
                           value=value, command=self.on_method_change).grid(row=0, column=i, sticky=tk.W, padx=(0, 20))
        
        # Color Settings (initially hidden)
        self.color_frame = ttk.LabelFrame(main_frame, text="Color Settings", padding="10")
        self.color_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(self.color_frame, text="Target Color (R,G,B):").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self.color_frame, textvariable=self.target_color, width=15).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        ttk.Label(self.color_frame, text="Tolerance:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        ttk.Scale(self.color_frame, from_=0, to=100, variable=self.tolerance_var, 
                 orient=tk.HORIZONTAL, length=150).grid(row=0, column=3, padx=(5, 0))
        ttk.Label(self.color_frame, textvariable=self.tolerance_var).grid(row=0, column=4, padx=(5, 0))
        
        # Hide color frame initially
        self.color_frame.grid_remove()
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.process_btn = ttk.Button(button_frame, text="Remove Background", 
                                     command=self.process_gif, state=tk.DISABLED)
        self.process_btn.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear", command=self.clear_all).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Exit", command=self.root.quit).grid(row=0, column=2)
        
        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(0, weight=1)
        
        self.progress_text = scrolledtext.ScrolledText(progress_frame, height=15, width=80)
        self.progress_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Select a GIF file to begin")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Bind events
        self.input_path.trace('w', self.on_input_change)
        
        # Initially hide color settings
        self.on_method_change()
    
    def browse_input(self):
        """Browse for input GIF file"""
        filename = filedialog.askopenfilename(
            title="Select GIF File",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)
            # Auto-generate output path
            output_path = create_output_path(filename)
            self.output_path.set(str(output_path))
    
    def browse_output(self):
        """Browse for output location"""
        filename = filedialog.asksaveasfilename(
            title="Save Output GIF As",
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
    
    def on_input_change(self, *args):
        """Enable/disable process button based on input"""
        if self.input_path.get() and Path(self.input_path.get()).exists():
            self.process_btn.config(state=tk.NORMAL)
            self.status_var.set("Ready to process - Click 'Remove Background'")
        else:
            self.process_btn.config(state=tk.DISABLED)
            self.status_var.set("Select a valid GIF file")
    
    def on_method_change(self):
        """Show/hide color settings based on method"""
        if self.method_var.get() == "color":
            self.color_frame.grid()
        else:
            self.color_frame.grid_remove()
    
    def get_gif_info(self):
        """Display information about the selected GIF"""
        if not self.input_path.get() or not Path(self.input_path.get()).exists():
            messagebox.showerror("Error", "Please select a valid GIF file first")
            return
        
        try:
            info = self.processor.get_gif_info(self.input_path.get())
            
            info_text = f"""📊 GIF Information:
File: {self.input_path.get()}
Frames: {info['frame_count']}
Size: {info['size']}
Mode: {info['mode']}
Animated: {info['is_animated']}
Duration: {info['duration']:.2f} seconds"""
            
            messagebox.showinfo("GIF Information", info_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get GIF info:\n{str(e)}")
    
    def clear_all(self):
        """Clear all fields"""
        self.input_path.set("")
        self.output_path.set("")
        self.progress_text.delete(1.0, tk.END)
        self.status_var.set("Ready - Select a GIF file to begin")
    
    def log_message(self, message):
        """Add message to progress text"""
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.root.update()
    
    def process_gif(self):
        """Process the GIF with background removal"""
        if self.is_processing:
            return
        
        # Validate inputs
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select an input GIF file")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify an output file path")
            return
        
        # Start processing in a separate thread
        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED)
        self.progress_bar.start()
        
        thread = threading.Thread(target=self._process_gif_thread)
        thread.daemon = True
        thread.start()
    
    def _process_gif_thread(self):
        """Background thread for GIF processing"""
        try:
            # Prepare parameters
            kwargs = {}
            if self.method_var.get() == 'color':
                try:
                    color_parts = self.target_color.get().split(',')
                    if len(color_parts) == 3:
                        kwargs['target_color'] = tuple(int(x.strip()) for x in color_parts)
                    else:
                        raise ValueError("Color should be in format: R,G,B")
                except ValueError as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Invalid color format: {e}"))
                    return
                kwargs['tolerance'] = self.tolerance_var.get()
            
            # Update UI
            self.root.after(0, lambda: self.log_message("🔄 Starting background removal..."))
            self.root.after(0, lambda: self.log_message(f"📁 Input: {self.input_path.get()}"))
            self.root.after(0, lambda: self.log_message(f"📁 Output: {self.output_path.get()}"))
            self.root.after(0, lambda: self.log_message(f"🎯 Method: {self.method_var.get()}"))
            
            if self.method_var.get() == 'color':
                self.root.after(0, lambda: self.log_message(f"🎨 Target color: {kwargs['target_color']}"))
                self.root.after(0, lambda: self.log_message(f"📏 Tolerance: {kwargs['tolerance']}"))
            
            # Extract frames
            self.root.after(0, lambda: self.log_message("\n📂 Extracting frames..."))
            frames, durations = self.processor.extract_frames(self.input_path.get())
            self.root.after(0, lambda: self.log_message(f"✅ Extracted {len(frames)} frames"))
            
            # Process frames
            self.root.after(0, lambda: self.log_message("\n🎨 Removing backgrounds..."))
            processed_frames = []
            
            for i, frame in enumerate(frames):
                processed_frame = self.remover.process_frame(frame, method=self.method_var.get(), **kwargs)
                processed_frames.append(processed_frame)
                
                # Update progress
                progress = (i + 1) / len(frames) * 100
                if i % 5 == 0 or i == len(frames) - 1:  # Update every 5 frames to reduce UI updates
                    self.root.after(0, lambda p=progress, idx=i: self._update_progress(p, idx, len(frames)))
            
            # Create output GIF
            self.root.after(0, lambda: self.log_message("\n💾 Saving output GIF..."))
            self.processor.create_gif(processed_frames, durations, self.output_path.get())
            
            # Show completion message
            self.root.after(0, self._process_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self._process_error(str(e)))
    
    def _update_progress(self, progress, current, total):
        """Update progress in UI thread"""
        self.log_message(f"  🖼️ Processed frame {current + 1}/{total} ({progress:.1f}%)")
    
    def _process_complete(self):
        """Handle process completion"""
        self.progress_bar.stop()
        self.is_processing = False
        self.process_btn.config(state=tk.NORMAL)
        
        # Show file sizes
        input_size = Path(self.input_path.get()).stat().st_size / 1024
        output_size = Path(self.output_path.get()).stat().st_size / 1024
        
        self.log_message(f"\n🎉 Processing Complete!")
        self.log_message(f"  ✅ Original: {self.input_path.get()}")
        self.log_message(f"  ✅ Processed: {self.output_path.get()}")
        self.log_message(f"  📦 File size: {input_size:.1f}KB → {output_size:.1f}KB")
        self.log_message(f"\n💡 Tip: Open the output file to check the results!")
        
        self.status_var.set("Processing complete!")
        
        # Ask if user wants to open the output file
        result = messagebox.askyesno("Success", 
                                   "Background removal completed successfully!\n\nWould you like to open the output file?")
        if result:
            try:
                os.startfile(self.output_path.get())  # Windows
            except:
                try:
                    import subprocess
                    subprocess.run(['open', self.output_path.get()])  # macOS
                except:
                    try:
                        subprocess.run(['xdg-open', self.output_path.get()])  # Linux
                    except:
                        messagebox.showinfo("Output File", f"File saved at:\n{self.output_path.get()}")
    
    def _process_error(self, error_message):
        """Handle processing errors"""
        self.progress_bar.stop()
        self.is_processing = False
        self.process_btn.config(state=tk.NORMAL)
        
        self.log_message(f"\n❌ Error: {error_message}")
        self.status_var.set("Processing failed!")
        
        messagebox.showerror("Processing Error", f"Background removal failed:\n{error_message}")

def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = GIFBackgroundRemoverGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()