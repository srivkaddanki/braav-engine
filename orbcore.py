import tkinter as tk
from tkinter import filedialog, scrolledtext
import os, shutil, threading, time
from dotenv import load_dotenv
from logger import logger

# # Import your Brain class
# from brain import BraavBrain
# # Import the watch directory from your watcher script
# from orb_watcher import OrbVoidHandler, DairyHandler, WATCH_DIR, DAIRY_WATCH_DIR
# from watchdog.observers import Observer

load_dotenv()

class OrbApp:
    def __init__(self, brain=None):
        self.brain = brain
        self.root = tk.Tk()
        self.root.title("ORB ENGINE | Agentic Interface")
        self.root.geometry("700x800")
        self.root.configure(bg="#121212")

        # 1. THE TRACE LOG (Observability)
        self.display = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, height=25, 
            bg="#1e1e1e", fg="#00ff41", 
            font=("Consolas", 10), insertbackground="white"
        )
        self.display.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.update_log(">>> System Initialized. Awaiting input...")

        # 2. THE INPUT AREA
        self.entry = tk.Text(
            self.root, height=6, bg="#2d2d2d", fg="white", 
            font=("Segoe UI", 12), padx=10, pady=10,
            insertbackground="white"
        )
        self.entry.pack(pady=5, padx=10, fill=tk.X)
        
        # Shortcut: Ctrl+Enter to process
        self.entry.bind('<Control-Return>', lambda e: self.process_query())

        # 3. BUTTONS
        btn_frame = tk.Frame(self.root, bg="#121212")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="📓 LOG DIARY", command=self.save_thought, 
                  bg="#3a3a3a", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="👁️ VISION SCAN", command=self.open_vision_dialog, 
                  bg="#4b0082", fg="white", width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🚀 PROCESS", command=self.process_query, 
                  bg="#007acc", fg="white", width=15).pack(side=tk.RIGHT, padx=5)

    def update_log(self, text):
        self.display.config(state=tk.NORMAL)
        self.display.insert(tk.END, f"\n{text}\n")
        self.display.see(tk.END)
        self.display.config(state=tk.DISABLED)

    def save_thought(self):
        val = self.entry.get("1.0", tk.END).strip()
        if val:
            logger.info(f"Saving thought: {val}")
            # status = self.brain.log_stream(val)
            # self.update_log(f"SYSTEM: {status}")
            self.entry.delete("1.0", tk.END)

    def process_query(self):
        val = self.entry.get("1.0", tk.END).strip()
        if val:
            self.update_log(f"USER: {val}")
            logger.info(f"Processing query: {val}")
            self.entry.delete("1.0", tk.END)
            # Threading prevents the UI from freezing during AI reasoning
            # threading.Thread(target=self._run_ai, args=(val,), daemon=True).start()

    def _run_ai(self, val):
        try:
            # Step 1: Trigger the Agentic Loop
            # res = self.brain.handle_query(val)
            # # Step 2: Use .after to safely update UI from background thread
            # self.root.after(0, lambda: self.update_log(f"ORB: {res}"))
            pass
        except Exception as e:
            # FIX: Capture error string immediately to avoid NameError closure bug
            error_str = str(e)
            logger.error(f"Error in AI loop: {error_str}", exc_info=True)
            self.root.after(0, lambda: self.update_log(f"KERNEL ERROR: {error_str}"))

    def open_vision_dialog(self):
        """Pick a photo of your diary and send it to the Vision Hand"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.update_log(f"VISION: Analyzing {os.path.basename(file_path)}...")
            logger.info(f"Analyzing image: {file_path}")
            # threading.Thread(target=self._run_vision, args=(file_path,), daemon=True).start()

    def _run_vision(self, path):
        try:
            # # Calls the vision_swallow function we added to brain.py
            # res = self.brain.vision_swallow(path)
            # self.root.after(0, lambda: self.update_log(res))
            pass
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error in vision loop: {error_str}", exc_info=True)
            self.root.after(0, lambda: self.update_log(f"VISION ERROR: {error_str}"))

# def start_watcher(brain):
#     def run_observer():
#         if not os.path.exists(WATCH_DIR):
#             os.makedirs(WATCH_DIR)
#         observer = Observer()
#         observer.schedule(OrbVoidHandler(brain), WATCH_DIR, recursive=False)
#         observer.start()
        
#         # Start dairy watcher on same observer
#         if not os.path.exists(DAIRY_WATCH_DIR):
#             os.makedirs(DAIRY_WATCH_DIR)
#         observer.schedule(DairyHandler(brain), DAIRY_WATCH_DIR, recursive=False)
        
#         logger.info(f"ORB_VOID watcher: {WATCH_DIR}")
#         logger.info(f"ORB_DAIRY watcher: {DAIRY_WATCH_DIR}")
#         logger.info("Watchers active and listening...")
#         try:
#             while True: time.sleep(1)
#         except: 
#             observer.stop()
#             logger.info("Watchers stopped.")
#     threading.Thread(target=run_observer, daemon=True).start()

if __name__ == "__main__":
    logger.info("=============================================")
    logger.info("LAUNCHING ORB ENGINE (Simplified)")
    logger.info("=============================================")
    
    # URL, KEY = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
    # if URL and KEY:
    #     logger.info("Environment vars loaded")
    #     my_brain = BraavBrain(URL, KEY)
    #     logger.info("Brain initialized")
        
    #     logger.info("Starting file watchers...")
    #     start_watcher(my_brain)
    #     logger.info("Watchers active on ORB_VOID and ORB_DAIRY")
    #     logger.info("=============================================")
    #     logger.info("ORB READY | Tkinter window opening...")
    #     logger.info("=============================================")
        
    app = OrbApp()
    app.root.mainloop()
    # else:
    #     logger.info("Missing SUPABASE_URL or SUPABASE_KEY in .env")