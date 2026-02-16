import tkinter as tk
from logger import logger

class SpeechBubble:
    def __init__(self, parent):
        self.root = tk.Toplevel(parent)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True, "-alpha", 0.0)
        self.root.config(bg='#000101')
        self.root.wm_attributes("-transparentcolor", '#000101')
        
        self.label = tk.Label(self.root, bg='#1e1e1e', fg='#4f86f7', padx=12, pady=8, wraplength=250)
        self.label.pack()

    def speak(self, text, x, y):
        logger.info(f"Speech bubble: {text}")
        self.label.config(text=text)
        self.root.update_idletasks()
        self.root.geometry(f"+{int(x)}+{int(y-50)}")
        self.fade_in()

    def fade_in(self):
        # ... (Your existing fade logic)
        self.root.attributes("-alpha", 1.0)