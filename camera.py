import cv2
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk
import os
import time


class WebcamApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Webcam Feed")

        self.video_source = 0  # Default webcam
        self.vid = cv2.VideoCapture(self.video_source)

        self.label = Label(self.window)
        self.label.pack()

        # # Capture button
        # self.capture_button = Button(self.window, text="Capture Image", command=self.capture_image, bg="gray25", fg="white")
        # self.capture_button.pack(pady=10)

        self.update_frame()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_frame(self):
        ret, frame = self.vid.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.label.config(image=self.photo)
            self.label.image = self.photo
        self.window.after(10, self.update_frame)

    def capture_image(self):
        ret, frame = self.vid.read()
        if ret:
            if not os.path.exists("captured"):
                os.makedirs("captured")
            filename = os.path.join("captured", f"capture_{time.strftime('%Y%m%d_%H%M%S')}.jpg")
            cv2.imwrite(filename, frame)
            print(f"✅ Image saved as {filename}")

    def on_closing(self):
        print("Releasing camera...")
        self.vid.release()
        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamApp(root)
    root.mainloop()
