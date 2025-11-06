import tkinter as tk
from tkinter import messagebox
import time
import random
import pymysql
import os
import cv2
from PIL import Image, ImageTk
from emotion_detector import detect_emotion


class SmartMirrorApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Smart Mirror Desktop")
        self.window.geometry("900x500")
        self.window.resizable(False, False)

        # MySQL Configuration
        self.db_host = "localhost"
        self.db_user = "root"
        self.db_pass = "1ms23ci012@msrit.edu"  # change if needed
        self.db_name = "smartmirror_db"

        # Fonts and colors
        self.font_large = ("Helvetica", 48, "bold")
        self.font_medium = ("Helvetica", 18)
        self.text_color = "white"

        # Load data files (fallback to root quotes.txt)
        potential = os.path.join("data", "quotes.txt")
        self.quotes_path = potential if os.path.exists(potential) else "quotes.txt"

        # Setup MySQL
        self._setup_db()

        # Setup camera feed as background
        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)
        self.bg_label = tk.Label(self.window)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.update_background()

        # Overlay widgets
        self.create_widgets()
        self.update_time()

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    # --- MySQL setup ---
    def _setup_db(self):
        conn = pymysql.connect(host=self.db_host, user=self.db_user, password=self.db_pass)
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS smartmirror_db")
        conn.commit()
        conn.close()

        conn = pymysql.connect(
            host=self.db_host, user=self.db_user, password=self.db_pass, database=self.db_name
        )
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                content TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def create_widgets(self):
        # Instead of a full-screen overlay, use a top bar so camera remains visible
        self.overlay = tk.Frame(self.window, bg="#000000")
        # limit height so it doesn't cover the camera view
        self.overlay.place(x=0, y=0, relwidth=1, height=140)

        title = tk.Label(self.overlay, text="Smart Mirror Dashboard",
                         fg="cyan", bg="#000000", font=self.font_medium)
        title.pack(pady=4)

        self.clock_label = tk.Label(self.overlay, font=self.font_large,
                                    fg=self.text_color, bg="#000000")
        self.clock_label.pack(pady=2)

        self.quote_label = tk.Label(self.overlay, text="", wraplength=700,
                                    fg="lightgreen", bg="#000000",
                                    font=self.font_medium, justify="center")
        self.quote_label.pack(pady=6)
        self.show_quote()

        # --- Controls frame (top-right) ---
        self.controls = tk.Frame(self.overlay, bg="#111111")
        self.controls.place(relx=1.0, x=-10, y=8, anchor="ne", width=200, height=120)

        # Capture button
        self.capture_button = tk.Button(self.controls, text="Capture Image", command=self.capture_image,
                                        bg="gray20", fg="white")
        self.capture_button.pack(pady=4, fill="x", padx=8)

        # Note entry + add button
        entry_frame = tk.Frame(self.controls, bg="#111111")
        entry_frame.pack(pady=2, fill="x", padx=8)
        self.note_entry = tk.Entry(entry_frame)
        self.note_entry.pack(side="left", expand=True, fill="x")
        self.add_note_button = tk.Button(entry_frame, text="+", width=2, command=self.add_note, bg="gray25", fg="white")
        self.add_note_button.pack(side="left", padx=4)

        # Load notes button
        self.load_notes_button = tk.Button(self.controls, text="Load Notes", command=self.load_notes,
                                           bg="gray20", fg="white")
        self.load_notes_button.pack(pady=4, fill="x", padx=8)

        # Small notes listbox on the right side below overlay
        self.notes_box = tk.Listbox(self.window, bg="#111111", fg="white")
        self.notes_box.place(x=700, y=150, width=190, height=320)

        # ensure overlay and controls are above the background label
        self.overlay.lift(self.bg_label)
        self.controls.lift()  # bring controls to top within the overlay
        self.notes_box.lift(self.bg_label)

    # --- Background update using webcam ---
    def update_background(self):
        ret, frame = self.vid.read()
        if ret:
            frame = cv2.flip(frame, 1)  # mirror effect
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (900, 500))
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.bg_label.imgtk = imgtk
            self.bg_label.configure(image=imgtk)
        self.window.after(30, self.update_background)

    # --- Clock updater ---
    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.clock_label.config(text=current_time)
        self.window.after(1000, self.update_time)

    # --- Quote handler ---
    def show_quote(self):
        try:
            with open(self.quotes_path, "r", encoding="utf-8") as f:
                quotes = [q.strip() for q in f.readlines() if q.strip()]
            quote = random.choice(quotes) if quotes else "Add quotes to quotes.txt"
            self.quote_label.config(text=f'"{quote}"')
        except FileNotFoundError:
            self.quote_label.config(text="No quotes found! Add some in data/quotes.txt or quotes.txt")

    # --- Add note ---
    def add_note(self):
        note = self.note_entry.get().strip()
        if not note:
            messagebox.showwarning("Empty Note", "Please enter a note before adding!")
            return

        conn = pymysql.connect(host=self.db_host, user=self.db_user,
                               password=self.db_pass, database=self.db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (content) VALUES (%s)", (note,))
        conn.commit()
        conn.close()

        self.note_entry.delete(0, tk.END)
        self.load_notes()

    # --- Capture image (new) ---
    def capture_image(self):
        ret, frame = self.vid.read()
        if ret:
            if not os.path.exists("captured"):
                os.makedirs("captured")
            filename = os.path.join("captured", f"capture_{time.strftime('%Y%m%d_%H%M%S')}.jpg")
            # save mirrored BGR frame (mirror for natural selfie)
            frame = cv2.flip(frame, 1)
            cv2.imwrite(filename, frame)
            print(f"✅ Image saved as {filename}")
            messagebox.showinfo("Capture", f"Image saved as {os.path.basename(filename)}")

    # --- Load notes ---
    def load_notes(self):
        conn = pymysql.connect(host=self.db_host, user=self.db_user,
                               password=self.db_pass, database=self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM notes")
        rows = cursor.fetchall()
        conn.close()

        self.notes_box.delete(0, tk.END)
        for row in rows:
            self.notes_box.insert(tk.END, row[0])

    # --- Exit ---
    def on_close(self):
        print("Releasing camera...")
        try:
            self.vid.release()
        except:
            pass
        self.window.destroy()

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = SmartMirrorApp()
    app.run()
