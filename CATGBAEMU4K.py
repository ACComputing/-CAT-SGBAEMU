import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import sys

# Import the compiled Cython core
try:
    import emu_core
except ImportError:
    messagebox.showerror("Error", "Cython core module not found.\nRun 'python setup.py build_ext --inplace' first.")
    sys.exit(1)

class GBAEmulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cat's GBA EMU")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Emulator instance
        self.emulator = emu_core.GBAEmulator()
        self.rom_path = None
        self.emulation_thread = None
        self.running = False

        # Button style: black background, blue text
        button_style = {
            "bg": "black",
            "fg": "blue",
            "activebackground": "gray",
            "activeforeground": "lightblue",
            "font": ("Arial", 10, "bold"),
            "width": 12,
            "height": 1
        }

        # Frame for buttons
        btn_frame = tk.Frame(root, bg="gray20")
        btn_frame.pack(pady=20)

        # Buttons
        self.load_btn = tk.Button(btn_frame, text="Load ROM", command=self.load_rom, **button_style)
        self.load_btn.grid(row=0, column=0, padx=5)

        self.start_btn = tk.Button(btn_frame, text="Start", command=self.start_emu, state=tk.DISABLED, **button_style)
        self.start_btn.grid(row=0, column=1, padx=5)

        self.pause_btn = tk.Button(btn_frame, text="Pause", command=self.pause_emu, state=tk.DISABLED, **button_style)
        self.pause_btn.grid(row=0, column=2, padx=5)

        self.stop_btn = tk.Button(btn_frame, text="Stop", command=self.stop_emu, state=tk.DISABLED, **button_style)
        self.stop_btn.grid(row=0, column=3, padx=5)

        self.reset_btn = tk.Button(btn_frame, text="Reset", command=self.reset_emu, state=tk.DISABLED, **button_style)
        self.reset_btn.grid(row=0, column=4, padx=5)

        # Status label
        self.status = tk.Label(root, text="No ROM loaded", bg="gray20", fg="white", font=("Arial", 9))
        self.status.pack(pady=10)

        # Canvas placeholder for video (in a real implementation you'd draw frames here)
        self.canvas = tk.Canvas(root, width=480, height=320, bg="black", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.canvas.create_text(240, 160, text="Cat's GBA EMU\nReady", fill="white", font=("Arial", 16), anchor="center")

        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_rom(self):
        path = filedialog.askopenfilename(
            title="Select GBA ROM",
            filetypes=[("GBA ROMs", "*.gba"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            self.emulator.load_rom(path.encode())
            self.rom_path = path
            self.status.config(text=f"Loaded: {path.split('/')[-1]}")
            self.enable_buttons(True)
            self.canvas.delete("all")
            self.canvas.create_text(240, 160, text="ROM loaded\nPress Start", fill="white", font=("Arial", 12), anchor="center")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load ROM:\n{e}")
            self.status.config(text="Load failed")

    def start_emu(self):
        if not self.rom_path:
            return
        if self.emulation_thread and self.emulation_thread.is_alive():
            # Already running, unpause
            self.emulator.start()
            self.status.config(text="Emulation running")
            return
        self.emulator.start()
        self.running = True
        self.status.config(text="Emulation running")
        self.emulation_thread = threading.Thread(target=self.emulation_loop, daemon=True)
        self.emulation_thread.start()
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        self.reset_btn.config(state=tk.NORMAL)

    def pause_emu(self):
        self.emulator.pause()
        self.running = False
        self.status.config(text="Paused")
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)

    def stop_emu(self):
        self.emulator.stop()
        self.running = False
        if self.emulation_thread:
            self.emulation_thread.join(timeout=0.5)
        self.status.config(text="Stopped")
        self.enable_buttons(False)

    def reset_emu(self):
        self.emulator.reset()
        self.status.config(text="Reset")

    def emulation_loop(self):
        """Run emulation frames in a background thread."""
        while self.running:
            self.emulator.step_frame()
            # Simple timing – not perfect, but keeps UI responsive
            time.sleep(1/60)

    def enable_buttons(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.start_btn.config(state=state)
        self.pause_btn.config(state=tk.DISABLED)  # pause only active after start
        self.stop_btn.config(state=state)
        self.reset_btn.config(state=state)

    def on_close(self):
        if self.running:
            self.emulator.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GBAEmulatorGUI(root)
    root.mainloop()
