import tkinter as tk
from tkinter import filedialog, ttk
import tkinter.scrolledtext as scrolled_text
from png_image import PNGImage
from block_cipher import ElectronicCodeBook, Counter
from PIL import Image, ImageTk


class GUI:
    BlockCiphers = {
        "ElectronicCodeBook": ElectronicCodeBook,
        "Counter": Counter,
    }

    def __init__(self):
        # main window #
        self.window = tk.Tk()
        self.window.geometry("1280x800")
        self.window.configure(background="black")
        # current image #
        self.png = PNGImage("data/dices.png")
        image = self.get_photo_image()
        # block cipher
        self.block_cipher = tk.StringVar()
        # widgets #
        # label with file path
        self.file_label = tk.Label(
            self.window,
            text=f"File path: {self.png.image_path}",
            bg="black",
            fg="white"
        )
        # label with Block Cipher
        self.bc_label = tk.Label(
            self.window,
            text="Block Cipher:",
            font="bold",
            bg="black",
            fg="white",
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
        # button for showing image, chunks (hidden)
        self.image_chunks_button = tk.Button(
            self.window,
            text="Image/Chunks",
            bg="black",
            fg="white",
            command=self.display_image_chunks
        )
        # button for showing fft
        self.fft_button = tk.Button(
            self.window,
            text="FFT",
            bg="black",
            fg="white",
            command=self.get_fft
        )
        # button for encrypting image
        self.encrypt_button = tk.Button(
            self.window,
            text="Encrypt",
            bg="black",
            fg="white",
            command=self.encrypt
        )
        # button for decrypting image
        self.decrypt_button = tk.Button(
            self.window,
            text="Decrypt",
            bg="black",
            fg="white",
            command=self.decrypt
        )
        # button for generating rsa keys
        self.rsa_gen_button = tk.Button(
            self.window,
            text="Generate Keys",
            bg="black",
            fg="white",
            command=self.generate_keys,
        )
        # block cipher combo_box
        self.block_cipher_cbox = ttk.Combobox(
            self.window,
            values=list(self.BlockCiphers.keys()),
            state="readonly",
            textvariable=self.block_cipher,
        )
        self.block_cipher_cbox.set(list(self.BlockCiphers.keys())[0])
        # displayed image
        self.image = tk.Label(
            self.window,
            image=image
        )
        self.image.image = image
        # fft magnitude image (hidden)
        self.fft_mag_image = tk.Label(self.window)
        # fft magnitude image (hidden)
        self.fft_phase_image = tk.Label(self.window)
        # text with parsed PNG chunks
        self.text_scroll = scrolled_text.ScrolledText(
            self.window,
            bg="black",
            fg="white"
        )
        self.text_scroll.insert(tk.INSERT, self.png.to_string())
        self.text_scroll.configure(state="disabled")
        # grid #
        self.file_label.grid(row=3, column=0, columnspan=4, sticky="W", padx=10, pady=10)
        self.bc_label.grid(row=1, column=1, padx=10, pady=10)
        self.file_button.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")
        self.anonymize_button.grid(row=1, column=0, padx=10, pady=10, sticky="NSEW")
        self.fft_button.grid(row=0, column=1, padx=10, pady=10, sticky="NSEW")
        self.image_chunks_button.grid(row=0, column=1, padx=10, pady=10, sticky="NSEW")
        self.encrypt_button.grid(row=0, column=2, padx=10, pady=10, sticky="NSEW")
        self.decrypt_button.grid(row=0, column=3, padx=10, pady=10, sticky="NSEW")
        self.rsa_gen_button.grid(row=1, column=3, padx=10, pady=10, sticky="NSEW")
        self.block_cipher_cbox.grid(row=1, column=2, padx=10, pady=10, sticky="NSEW")
        self.image.grid(row=2, column=0, columnspan=4, padx=10)
        self.text_scroll.grid(row=2, column=4, columnspan=2, padx=10, sticky="NSEW")
        # main loop #
        self.window.mainloop()

    def get_photo_image(self):
        image = self.png.get_image()
        image.thumbnail((640, 720), Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)

    def anonymize_image(self):
        self.png.anonymize("data/out.png")  # self.png.image_path
        self.png = PNGImage("data/out.png")  # self.png.image_path
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

    def get_fft(self):
        magnitude, phase = self.png.fft()
        magnitude.thumbnail((640, 720), Image.ANTIALIAS)
        phase.thumbnail((640, 720), Image.ANTIALIAS)
        magnitude = ImageTk.PhotoImage(magnitude)
        phase = ImageTk.PhotoImage(phase)
        self.fft_mag_image.configure(image=magnitude)
        self.fft_phase_image.configure(image=phase)
        self.fft_mag_image.image = magnitude
        self.fft_phase_image.image = phase
        self.display_fft()

    def display_fft(self):
        self.image.grid_forget()
        self.text_scroll.grid_forget()
        self.fft_button.grid_forget()
        self.fft_mag_image.grid(row=2, column=0, columnspan=4, padx=10)
        self.fft_phase_image.grid(row=2, column=4, columnspan=2, padx=10)
        self.image_chunks_button.grid(row=0, column=1, padx=10, pady=10, sticky="NSEW")

    def display_image_chunks(self):
        self.fft_mag_image.grid_forget()
        self.fft_phase_image.grid_forget()
        self.image_chunks_button.grid_forget()
        self.image.grid(row=2, column=0, columnspan=4, padx=10)
        self.text_scroll.grid(row=2, column=4, columnspan=2, padx=10, sticky="NSEW")
        self.fft_button.grid(row=0, column=1, padx=10, pady=10, sticky="NSEW")

    def browse_files(self):
        filename = tk.filedialog.askopenfilename(title="Select file", filetypes=[("image files", ".png")])
        if filename == "":
            return
        self.png = PNGImage(filename)
        self.update_image()
        self.update_scroll_text()
        self.file_label.configure(text=f"File path: {filename}")
        self.display_image_chunks()

    def encrypt(self):
        self.png.encrypt(1024, cipher_block=self.BlockCiphers[self.block_cipher.get()])
        self.update_image()

    def decrypt(self):
        self.png.decrypt(1024, cipher_block=self.BlockCiphers[self.block_cipher.get()])
        self.update_image()

    def generate_keys(self):
        pass
