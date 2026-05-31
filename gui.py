import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import os
import sys
import shutil # Added for deleting directories

class AnimationPipelineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP8266 OLED Animation Builder")
        self.root.geometry("600x680") # Slightly increased height for the new checkbox
        self.root.resizable(False, False)
        
        # Where the code generator drops the final file
        self.final_ino_path = os.path.join(os.getcwd(), "animation_updated", "animation_updated.ino")

        # Variables
        self.gif_path = tk.StringVar()
        self.target_width = tk.IntVar(value=128)
        self.target_height = tk.IntVar(value=64)
        self.invert_pixels = tk.BooleanVar(value=False)
        self.auto_cleanup = tk.BooleanVar(value=True) # New variable for auto-deletion

        self.apply_modern_theme()
        self.setup_ui()

    def apply_modern_theme(self):
        """Forces Tkinter out of the 2000s and into a clean dark mode."""
        self.root.configure(bg="#1e1e2e")
        style = ttk.Style()
        
        style.theme_use('clam')
        
        # Global Configurations
        style.configure(".", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10))
        style.configure("TFrame", background="#1e1e2e")
        
        # Entry Boxes
        style.configure("TEntry", fieldbackground="#313244", foreground="#cdd6f4", borderwidth=0, padding=5)
        
        # Label Frames (Cards)
        style.configure("TLabelframe", background="#1e1e2e", borderwidth=1, bordercolor="#45475a")
        style.configure("TLabelframe.Label", background="#1e1e2e", foreground="#89b4fa", font=("Segoe UI", 11, "bold"))
        
        # Standard Buttons
        style.configure("TButton", background="#313244", foreground="#cdd6f4", borderwidth=0, focuscolor="#1e1e2e", padding=6, font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[('active', '#45475a'), ('pressed', '#585b70')])
        
        # Accent Buttons (Run All)
        style.configure("Accent.TButton", background="#89b4fa", foreground="#11111b", borderwidth=0, padding=8, font=("Segoe UI", 11, "bold"))
        style.map("Accent.TButton", background=[('active', '#b4befe'), ('pressed', '#cba6f7')])
        
        # Action Buttons (Copy/Open)
        style.configure("Action.TButton", background="#a6e3a1", foreground="#11111b", borderwidth=0, padding=6, font=("Segoe UI", 10, "bold"))
        style.map("Action.TButton", background=[('active', '#94e2d5'), ('disabled', '#45475a')])

        # Checkboxes
        style.configure("TCheckbutton", background="#1e1e2e", foreground="#cdd6f4", focuscolor="#1e1e2e")
        style.map("TCheckbutton", background=[('active', '#1e1e2e')])

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Step 1: Input Settings ---
        input_frame = ttk.LabelFrame(main_frame, text=" ⚙ Configuration ", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 15))

        # Dynamic column configuration so the text entry resizes instead of cutting off the button
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Source GIF:").grid(row=0, column=0, sticky=tk.W, pady=8)
        ttk.Entry(input_frame, textvariable=self.gif_path).grid(row=0, column=1, sticky=tk.EW, padx=10)
        ttk.Button(input_frame, text="Browse", command=self.browse_gif, width=10).grid(row=0, column=2)

        ttk.Label(input_frame, text="Width (px):").grid(row=1, column=0, sticky=tk.W, pady=8)
        ttk.Entry(input_frame, textvariable=self.target_width, width=10).grid(row=1, column=1, sticky=tk.W, padx=10)

        ttk.Label(input_frame, text="Height (px):").grid(row=2, column=0, sticky=tk.W, pady=8)
        ttk.Entry(input_frame, textvariable=self.target_height, width=10).grid(row=2, column=1, sticky=tk.W, padx=10)

        ttk.Checkbutton(input_frame, text="Invert Pixels (Black/White Swap)", variable=self.invert_pixels).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(8, 0))
        
        # NEW: Auto-cleanup toggle
        ttk.Checkbutton(input_frame, text="Auto-delete temp folders after build (input_images & output_headers)", variable=self.auto_cleanup).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(8, 0))


        # --- Step 2: Controls ---
        control_frame = ttk.LabelFrame(main_frame, text=" 🚀 Execution ", padding="15")
        control_frame.pack(fill=tk.X, pady=(0, 15))

        steps_frame = ttk.Frame(control_frame)
        steps_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(steps_frame, text="1. Split GIF", command=self.run_splitter).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(steps_frame, text="2. Generate Frames", command=self.run_generator).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(steps_frame, text="3. Build Code", command=self.run_builder).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        ttk.Button(control_frame, text="▶ RUN FULL PIPELINE", command=self.run_all, style="Accent.TButton").pack(fill=tk.X, pady=5)

        # --- Output Console ---
        console_frame = ttk.LabelFrame(main_frame, text=" 💻 Terminal Output ", padding="5")
        console_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, height=8, state='disabled', bg="#11111b", fg="#a6e3a1", font=("Consolas", 9), insertbackground="white", borderwidth=0)
        self.console.pack(fill=tk.BOTH, expand=True)

        # --- Post Build Actions ---
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X)

        self.btn_copy = ttk.Button(action_frame, text="📋 Copy INO to Clipboard", command=self.copy_to_clipboard, style="Action.TButton", state=tk.DISABLED)
        self.btn_copy.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.btn_open = ttk.Button(action_frame, text="📝 Open in Editor", command=self.open_in_editor, style="Action.TButton", state=tk.DISABLED)
        self.btn_open.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

    def log(self, message):
        self.console.config(state='normal')
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.console.config(state='disabled')
        self.root.update()

    def browse_gif(self):
        init_dir = os.path.join(os.getcwd(), "input_videos") if os.path.exists("input_videos") else os.getcwd()
        filepath = filedialog.askopenfilename(initialdir=init_dir, filetypes=[("GIF Files", "*.gif"), ("All Files", "*.*")])
        if filepath:
            self.gif_path.set(filepath)

    def execute_script(self, script_name, extra_args=None):
        if not os.path.exists(script_name):
            self.log(f"[ERROR] Could not find {script_name}.")
            return False

        cmd = [sys.executable, script_name]
        if extra_args:
            cmd.extend(extra_args)

        self.log(f"--- Running {script_name} ---")
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                self.log(line.strip())
            process.wait()
            
            if process.returncode == 0:
                self.log(f"[SUCCESS] {script_name} completed.\n")
                return True
            else:
                self.log(f"[FAILED] {script_name} crashed (Code {process.returncode}).\n")
                return False
        except Exception as e:
            self.log(f"[ERROR] {str(e)}\n")
            return False

    def enable_actions(self):
        """Enables the copy/open buttons if the INO file exists."""
        if os.path.exists(self.final_ino_path):
            self.btn_copy.config(state=tk.NORMAL)
            self.btn_open.config(state=tk.NORMAL)
        else:
            self.log(f"[WARNING] Expected output at '{self.final_ino_path}' but didn't find it.")

    def copy_to_clipboard(self):
        try:
            with open(self.final_ino_path, 'r', encoding='utf-8') as f:
                code = f.read()
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            self.log("[INFO] Code successfully copied to clipboard.")
        except Exception as e:
            self.log(f"[ERROR] Failed to read INO file: {e}")

    def open_in_editor(self):
        try:
            if sys.platform.startswith('linux'):
                # Opens in default Linux editor (gedit, nano, etc)
                subprocess.Popen(['xdg-open', self.final_ino_path])
            elif sys.platform == 'win32':
                # Explicitly force Notepad on Windows
                subprocess.Popen(['notepad.exe', self.final_ino_path])
            elif sys.platform == 'darwin': 
                # Explicitly force TextEdit on macOS
                subprocess.Popen(['open', '-e', self.final_ino_path])
            
            self.log("[INFO] Opening INO file in text editor.")
        except Exception as e:
            self.log(f"[ERROR] Could not launch editor: {e}")

    def cleanup_temp_files(self):
        """Deletes the temporary processing directories."""
        temp_folders = ["input_images", "output_headers"]
        cleaned_any = False
        
        for folder in temp_folders:
            folder_path = os.path.join(os.getcwd(), folder)
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path) # Recursively deletes the directory and all contents
                    self.log(f"[CLEANUP] Deleted '{folder}' directory.")
                    cleaned_any = True
                except Exception as e:
                    self.log(f"[ERROR] Could not delete '{folder}': {e}")
                    
        if cleaned_any:
            self.log("[INFO] Workspace successfully cleaned.\n")

    # --- Runners ---
    def run_splitter(self):
        selected_gif = self.gif_path.get()
        if not selected_gif:
            self.log("[ERROR] Please select a GIF file first!")
            return False
        return self.execute_script("image_splitter.py", [selected_gif])

    def run_generator(self):
        args = [str(self.target_width.get()), str(self.target_height.get()), str(self.invert_pixels.get())]
        return self.execute_script("frame_generator.py", args)

    def run_builder(self):
        success = self.execute_script("code_generator.py")
        if success:
            self.enable_actions()
            # If auto-cleanup is checked, run the cleanup method
            if self.auto_cleanup.get():
                self.cleanup_temp_files()
        return success

    def run_all(self):
        self.log("=== STARTING FULL PIPELINE ===\n")
        self.btn_copy.config(state=tk.DISABLED)
        self.btn_open.config(state=tk.DISABLED)
        
        if self.run_splitter():
            if self.run_generator():
                if self.run_builder():
                    self.log("=== PIPELINE FINISHED SUCCESSFULLY ===")

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimationPipelineGUI(root)
    root.mainloop()
