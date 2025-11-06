import tkinter as tk
from tkinter import messagebox
import time
import random
import pymysql
import os
from emotion_detector import detect_emotion


class SmartMirrorApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Smart Mirror Desktop")
        self.window.geometry("900x500")
        self.window.config(bg="black")
        self.window.resizable(False, False)

        # MySQL Configuration
        self.db_host = "localhost"
        self.db_user = "root"
        self.db_pass = "1ms23ci012@msrit.edu"
        self.db_name = "smartmirror_db"

        # Fonts and colors
        self.font_large = ("Helvetica", 48, "bold")
        self.font_medium = ("Helvetica", 18)
        self.font_small = ("Helvetica", 12)
        self.text_color = "white"

        # Load data files
        self.quotes_path = os.path.join("data", "quotes.txt")

        # Setup MySQL database
        self._setup_db()

        # UI elements
        self.create_widgets()
        self.update_time()

    # ✅ Create DB and table if not exists
    def _setup_db(self):
        # First connect without specifying DB (to create DB)
        conn = pymysql.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_pass
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS smartmirror_db")
        conn.commit()
        conn.close()

        # Now connect to the actual DB and create notes table
        conn = pymysql.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_pass,
            database=self.db_name
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

    # --- Create UI layout ---
    def create_widgets(self):
        title = tk.Label(self.window, text="Smart Mirror Dashboard",
                         fg="cyan", bg="black", font=self.font_medium)
        title.pack(pady=10)

        self.clock_label = tk.Label(self.window, font=self.font_large,
                                    fg=self.text_color, bg="black")
        self.clock_label.pack(pady=10)

        self.quote_label = tk.Label(self.window, text="", wraplength=700,
                                    fg="lightgreen", bg="black",
                                    font=self.font_medium, justify="center")
        self.quote_label.pack(pady=15)
        self.show_quote()

        self.notes_label = tk.Label(self.window, text="Your Notes:",
                                    fg="cyan", bg="black", font=self.font_medium)
        self.notes_label.pack(pady=5)

        self.notes_box = tk.Listbox(self.window, height=6, width=70,
                                    bg="gray15", fg="white")
        self.notes_box.pack(pady=5)
        self.load_notes()

        self.note_entry = tk.Entry(self.window, width=60)
        self.note_entry.pack(pady=5)

        add_btn = tk.Button(self.window, text="Add Note",
                            command=self.add_note, bg="gray25", fg="white")
        add_btn.pack(pady=5)

        quote_btn = tk.Button(self.window, text="New Quote",
                              command=self.show_quote, bg="gray25", fg="white")
        quote_btn.pack(pady=5)

        mood_btn = tk.Button(self.window, text="Check My Mood",
                             command=detect_emotion, bg="gray25", fg="white")
        mood_btn.pack(pady=5)

    # --- Clock updater ---
    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.clock_label.config(text=current_time)
        self.window.after(1000, self.update_time)

    # --- Quote handler ---
    def show_quote(self):
        try:
            with open(self.quotes_path, "r", encoding="utf-8") as f:
                quotes = f.readlines()
            quote = random.choice(quotes).strip()
            self.quote_label.config(text=f'"{quote}"')
        except FileNotFoundError:
            self.quote_label.config(text="No quotes found! Add some in data/quotes.txt")

    # --- Notes loading from MySQL ---
    def load_notes(self):
        conn = pymysql.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_pass,
            database=self.db_name
        )
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM notes")
        rows = cursor.fetchall()
        conn.close()

        self.notes_box.delete(0, tk.END)
        for row in rows:
            self.notes_box.insert(tk.END, row[0])

    # --- Add note to MySQL ---
    def add_note(self):
        note = self.note_entry.get().strip()
        if not note:
            messagebox.showwarning("Empty Note", "Please enter a note before adding!")
            return

        conn = pymysql.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_pass,
            database=self.db_name
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (content) VALUES (%s)", (note,))
        conn.commit()
        conn.close()

        self.note_entry.delete(0, tk.END)
        self.load_notes()

    def run(self):
        self.window.mainloop()
