import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import tkinter.scrolledtext as scrolled_text
from png_image import PNGImage
from block_cipher import ElectronicCodeBook, Counter
from PIL import Image, ImageTk
from rsa import MyRSA


class GUI:
    BlockCiphers = {
        "ElectronicCodeBook": ElectronicCodeBook,
        "Counter": Counter,
    }

    RsaKeySize = {
        "1024": 1024,
        "2048": 2048,
        "4096": 4096,
    }

    def __init__(self):
        # main window #
        self.window = tk.Tk()
        self.window.geometry("1345x800")
        self.window.configure(background="black")
        # current image #
        self.png = PNGImage("data/dices.png")
        self.rsa = None
        image = self.get_photo_image()
        # block cipher
        self.block_cipher = tk.StringVar()
        # rsa key_size
        self.rsa_size = tk.StringVar()
        # rsa selection
        self.rsa_selection = tk.IntVar()
        # widgets #
        # label with file path
        self.file_label = tk.Label(
            self.window,
            text=f"File path: {self.png.image_path}",
            font=("Helvetica", "12", "bold"),
            bg="black",
            fg="white"
        )
        # label with Block Cipher
        self.bc_label = tk.Label(
            self.window,
            text="Block Cipher:",
            font=("Helvetica", "14", "bold"),
            bg="black",
            fg="white",
        )
        # label with RSA key size
        self.rsa_size_label = tk.Label(
            self.window,
            text="Key Size:",
            font=("Helvetica", "14", "bold"),
            bg="black",
            fg="white",
        )
        # label with modulus
        self.mod_key_label = tk.Label(
            self.window,
            text="Modulus:",
            font=("Helvetica", "14", "bold"),
            bg="black",
            fg="white",
        )
        # label with public key exponent
        self.pub_key_exp = tk.Label(
            self.window,
            text="Public Exponent:",
            font=("Helvetica", "14", "bold"),
            bg="black",
            fg="white",
        )
        # label with private key exponent
        self.pvt_key_exp = tk.Label(
            self.window,
            text="Private Exponent:",
            font=("Helvetica", "14", "bold"),
            bg="black",
            fg="white",
        )
        # entry with modulus
        self.mod_entry = tk.Entry(
            font=("Helvetica", "12", "bold"),
        )
        # entry with public key exponent
        self.pub_key_entry = tk.Entry(
            font=("Helvetica", "12", "bold"),
        )
        # entry with private key exponent
        self.pvt_key_entry = tk.Entry(
            font=("Helvetica", "12", "bold"),
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
            font=("Helvetica", "12", "bold"),
            textvariable=self.block_cipher,
        )
        self.block_cipher_cbox.set(list(self.BlockCiphers.keys())[0])
        # rsa key size combo_box
        self.rsa_size_cbox = ttk.Combobox(
            self.window,
            values=list(self.RsaKeySize.keys()),
            state="readonly",
            font=("Helvetica", "12", "bold"),
            textvariable=self.rsa_size,
        )
        self.rsa_size_cbox.set(list(self.RsaKeySize.keys())[0])
        # rsa selection radio buttons
        self.rsa_radio_buttons = [
            tk.Radiobutton(self.window, text="MyRSA", variable=self.rsa_selection, value=1, font=("Helvetica", "10", "bold")),
            tk.Radiobutton(self.window, text="PyRSA", variable=self.rsa_selection, value=2, font=("Helvetica", "10", "bold")),
        ]
        for button in self.rsa_radio_buttons:
            button.configure(background="black", foreground="azure3", activebackground="black", activeforeground="white")
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
        self.file_label.grid(row=4, column=0, columnspan=4, sticky="W", padx=10, pady=10)
        self.bc_label.grid(row=2, column=1, padx=10, pady=10)
        self.rsa_size_label.grid(row=1, column=1, padx=10, pady=10)
        self.mod_key_label.grid(row=0, column=4, padx=10, pady=10)
        self.pub_key_exp.grid(row=1, column=4, padx=10, pady=10)
        self.pvt_key_exp.grid(row=2, column=4, padx=10, pady=10)
        self.mod_entry.grid(row=0, column=5, padx=10, pady=10, sticky="NSEW")
        self.pub_key_entry.grid(row=1, column=5, padx=10, pady=10, sticky="NSEW")
        self.pvt_key_entry.grid(row=2, column=5, padx=10, pady=10, sticky="NSEW")
        self.file_button.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")
        self.anonymize_button.grid(row=1, column=0, padx=10, pady=10, sticky="NSEW")
        self.rsa_radio_buttons[0].grid(row=0, column=1, padx=10, pady=10, sticky="W")
        self.rsa_radio_buttons[1].grid(row=0, column=1, padx=10, pady=10, sticky="E")
        self.fft_button.grid(row=2, column=0, padx=10, pady=10, sticky="NSEW")
        self.image_chunks_button.grid(row=2, column=0, padx=10, pady=10, sticky="NSEW")
        self.encrypt_button.grid(row=0, column=2, padx=10, pady=10, sticky="NSEW")
        self.decrypt_button.grid(row=0, column=3, padx=10, pady=10, sticky="NSEW")
        self.rsa_gen_button.grid(row=1, column=3, padx=10, pady=10, sticky="NSEW")
        self.rsa_size_cbox.grid(row=1, column=2, padx=10, pady=10, sticky="NSEW")
        self.block_cipher_cbox.grid(row=2, column=2, padx=10, pady=10, sticky="NSEW")
        self.image.grid(row=3, column=0, columnspan=4, padx=10)
        self.text_scroll.grid(row=3, column=4, columnspan=2, padx=10, sticky="NSEW")

        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)
        self.window.columnconfigure(2, weight=1)
        self.window.columnconfigure(3, weight=1)
        self.window.columnconfigure(4, weight=1)
        self.window.columnconfigure(5, weight=3)
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
        self.fft_mag_image.grid(row=3, column=0, columnspan=4, padx=10)
        self.fft_phase_image.grid(row=3, column=4, columnspan=2, padx=10)
        self.image_chunks_button.grid(row=2, column=0, padx=10, pady=10, sticky="NSEW")

    def display_image_chunks(self):
        self.fft_mag_image.grid_forget()
        self.fft_phase_image.grid_forget()
        self.image_chunks_button.grid_forget()
        self.image.grid(row=3, column=0, columnspan=4, padx=10)
        self.text_scroll.grid(row=3, column=4, columnspan=2, padx=10, sticky="NSEW")
        self.fft_button.grid(row=2, column=0, padx=10, pady=10, sticky="NSEW")

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
        if not self.rsa:
            return messagebox.showinfo('Error', 'Keys not generated')
        if not self._update_keys():
            return
        self.png.encrypt(rsa=self.rsa, cipher_block=self.BlockCiphers[self.block_cipher.get()])
        self.update_image()

    def decrypt(self):
        if not self.rsa:
            return messagebox.showinfo('Error', 'Keys not generated')
        if not self._update_keys():
            return
        self.png.decrypt(rsa=self.rsa, cipher_block=self.BlockCiphers[self.block_cipher.get()])
        self.update_image()

    def _update_keys(self):
        try:
            self.rsa.set_keys(int(self.mod_entry.get()), int(self.pub_key_entry.get()), int(self.pvt_key_entry.get()))
        except ValueError:
            messagebox.showinfo('Error', 'Some key is not an integer')
            return False
        return True

    def generate_keys(self):
        num_bits = self.RsaKeySize[self.rsa_size.get()]
        match self.rsa_selection.get():
            case 1:
                self.rsa = MyRSA(num_bits)
            case 2:
                self.rsa = MyRSA(num_bits)
            case _:
                return messagebox.showinfo('Error', 'RSA not selected')

        self.rsa.set_keys(*self.rsa.generate_keys())
        self.mod_entry.insert(0, str(self.rsa.mod))
        self.pub_key_entry.insert(0, str(self.rsa.pub_exp))
        self.pvt_key_entry.insert(0, str(self.rsa.pvt_exp))
