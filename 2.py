import tkinter as tk
import time
import random

def update_time():
    current_time = time.strftime("%H:%M:%S")
    clock_label.config(text=current_time)
    window.after(1000, update_time)

def show_quote():
    with open("quotes.txt", "r") as f:
        quotes = f.readlines()
    quote_label.config(text=random.choice(quotes).strip())

window = tk.Tk()
window.title("Smart Mirror Desktop")
window.geometry("800x480")
window.config(bg="black")

clock_label = tk.Label(window, font=("Helvetica", 50), fg="white", bg="black")
clock_label.pack(pady=20)

quote_label = tk.Label(window, font=("Helvetica", 16), fg="cyan", bg="black", wraplength=700)
quote_label.pack(pady=20)

update_time()
show_quote()

window.mainloop()
