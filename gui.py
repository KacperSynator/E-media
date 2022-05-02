import tkinter as tk
from tkinter import filedialog
import tkinter.scrolledtext as scrolled_text
from png_image import PNGImage
from PIL import Image, ImageTk


class GUI:
    def __init__(self):
        # main window #
        self.window = tk.Tk()
        self.window.geometry("1280x800")
        self.window.configure(background="black")
        # current image #
        self.png = PNGImage("data/dices.png")
        image = self.get_photo_image()
        # widgets #
        # label with file path
        self.file_label = tk.Label(
            self.window,
            text=f"File path: {self.png.image_path}",
            bg="black",
            fg="white"
        )
        # button for browsing files
        self.file_button = tk.Button(
            self.window,
            text="Browse files",
            bg="black",
            fg="white",
            command=self.browse_files
        )
        # button to anonymize images
        self.anonymize_button = tk.Button(
            self.window,
            text="Anonymize",
            bg="black",
            fg="white",
            command=self.anonymize_image
        )
        # displayed image
        self.image = tk.Label(
            self.window,
            image=image
        )
        self.image.image = image
        # text with parsed PNG chunks
        self.text_scroll = scrolled_text.ScrolledText(
            self.window,
            bg="black",
            fg="white"
        )
        self.text_scroll.insert(tk.INSERT, self.png.to_string())
        self.text_scroll.configure(state="disabled")
        # grid #
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)
        self.window.columnconfigure(2, weight=20)
        self.file_label.grid(row=2, column=0, columnspan=4, sticky="W", padx=10, pady=10)
        self.file_button.grid(row=0, column=0, padx=10, pady=10)
        self.anonymize_button.grid(row=0, column=1, padx=10, pady=10)
        self.image.grid(row=1, column=0, columnspan=3, padx=10)
        self.text_scroll.grid(row=1, column=3, sticky="NSEW")
        # main loop #
        self.window.mainloop()

    def get_photo_image(self):
        image = self.png.get_image()
        image.thumbnail((640, 720), Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)

    def anonymize_image(self):
        self.png.anonymize(self.png.image_path)
        self.png = PNGImage(self.png.image_path)
        self.update_scroll_text()

    def update_image(self):
        image = self.get_photo_image()
        self.image.configure(image=image)
        self.image.image = image

    def update_scroll_text(self):
        self.text_scroll.configure(state="normal")
        self.text_scroll.delete(1.0, tk.END)
        self.text_scroll.insert(tk.INSERT, self.png.to_string())
        self.text_scroll.configure(state="disabled")

    def browse_files(self):
        filename = tk.filedialog.askopenfilename(title="Select file", filetypes=[("image files", ".png")])
        self.png = PNGImage(filename)
        self.update_image()
        self.update_scroll_text()
        self.file_label.configure(text=f"File path: {filename}")

