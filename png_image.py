from PIL import Image
import numpy as np
from chunks import Chunk


class PNGImage:
    def __init__(self, image_path: str):
        with open(image_path, "rb") as input_image:
            content = [a for a in input_image.read()]
        self.image_path = image_path
        self.header = content[0:8]
        self.chunks = []
        self._read_chunks(content[8:])

    def _read_chunks(self, image: list[int]):
        start_idx, end_idx = 0, 0
        while end_idx < len(image):
            chunk_length = int.from_bytes(image[start_idx: start_idx + 4], byteorder="big")
            end_idx = start_idx + 12 + chunk_length  # 12 = length + name + crc (each 4 bytes)
            self.chunks.append(Chunk(image[start_idx: end_idx]))
            start_idx = end_idx

    def display_data(self, hide_raw_data=True):
        header_name = "".join([chr(c) for c in self.header[1:4]])
        print(f"Header: {header_name}\n\t raw: {self.header}")
        for chunk in self.chunks:
            chunk.display(hide_raw_data)

    def display_image(self):
        image = Image.open(self.image_path)
        image.show()

    def fft(self):
        im = Image.open(self.image_path).convert("L")
        np_im = np.asarray(im)

        img_fft = np.fft.fft2(np_im)
        shifted_fft = np.fft.fftshift(img_fft)
        magnitude, phase = np.abs(shifted_fft), np.angle(shifted_fft)
        magnitude = 20 * np.log(magnitude)
        phase = 255 * (phase - phase.min()) / (phase.max() - phase.min())
        magnitude = 255 * (magnitude - magnitude.min()) / (magnitude.max() - magnitude.min())
        print(magnitude)

        magnitude = Image.fromarray(magnitude.astype(np.uint8), "L")
        phase = Image.fromarray(phase.astype(np.uint8), "L")

        magnitude.show()
        phase.show()
