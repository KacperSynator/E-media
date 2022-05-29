from PIL import Image, ImageFile
import numpy as np
from chunks import Chunk
from rsa import MyRSA
from block_cipher import ElectronicCodeBook
# ImageFile.LOAD_TRUNCATED_IMAGES = True

class PNGImage:
    def __init__(self, image_path: str):
        with open(image_path, "rb") as input_image:
            content = [a for a in input_image.read()]
        self.image_path = image_path
        self.header = content[0:8]
        self.chunks = []
        self._read_chunks(content[8:])
        self._rsa = None

    def _read_chunks(self, image: list[int]):
        start_idx, end_idx = 0, 0
        while end_idx < len(image):
            chunk_length = int.from_bytes(image[start_idx: start_idx + 4], byteorder="big")
            end_idx = start_idx + 12 + chunk_length  # 12 = length + name + crc (each 4 bytes)
            self.chunks.append(Chunk(image[start_idx: end_idx]))
            start_idx = end_idx

    def display_data(self, hide_raw_data=True):
        print(self.to_string(hide_raw_data=hide_raw_data))

    def to_string(self, hide_raw_data=True):
        header_name = "".join([chr(c) for c in self.header[1:4]])
        result = f"Header: {header_name}\n\t raw: {self.header}\n"
        result += "\n--------------------------------------------------------------------------------\n\n"
        for chunk in self.chunks:
            result += chunk.to_sting(hide_raw_data)
            result += "\n--------------------------------------------------------------------------------\n\n"
        return result

    def display_image(self):
        image = Image.open(self.image_path)
        image.show()

    def get_image(self) -> Image:
        return Image.open(self.image_path)

    def anonymize(self, out_file: str):
        critical_chunks = list(filter(lambda chunk: chunk.name in ["IHDR", "IEND", "PLTE", "IDAT"], self.chunks))
        critical_chunks = list(map(lambda chunk: chunk.raw, critical_chunks))
        with open(out_file, "wb") as file:
            file.write(bytearray(self.header))
            for chunk in critical_chunks:
                file.write(bytearray(chunk))

    def fft(self):
        im = Image.open(self.image_path).convert("L")
        np_im = np.asarray(im)

        img_fft = np.fft.fft2(np_im)
        shifted_fft = np.fft.fftshift(img_fft)
        magnitude, phase = np.abs(shifted_fft), np.angle(shifted_fft)
        magnitude = 20 * np.log(magnitude)
        # phase = 255 * (phase - phase.min()) / (phase.max() - phase.min())
        # magnitude = 255 * (magnitude - magnitude.min()) / (magnitude.max() - magnitude.min())

        phase *= 255 / phase.max()
        magnitude *= 255 / magnitude.max()
        # phase = np.abs(phase)
        magnitude = np.abs(magnitude)

        magnitude = Image.fromarray(magnitude.astype(np.uint8), "L")
        phase = Image.fromarray(phase.astype(np.uint8), "L")

        return magnitude, phase

    def encrypt(self, number_of_bits):
        if not self._rsa:
            self._rsa = MyRSA(number_of_bits)
        idat_chunks = list(filter(lambda chunk: chunk.name == "IDAT", self.chunks))
        for chunk in idat_chunks:
            encrypted_data = self._encrypt_chunk_data(chunk.raw)
            chunk.raw = len(encrypted_data).to_bytes(4, "big") + bytearray(chunk.raw[4:8]) + encrypted_data + bytearray(chunk.raw[-4:])
            chunk.update_crc()

    def decrypt(self, number_of_bits):
        if not self._rsa:
            self._rsa = MyRSA(number_of_bits)
        idat_chunks = list(filter(lambda chunk: chunk.name == "IDAT", self.chunks))
        for chunk in idat_chunks:
            decrypted_data = self._decrypt_chunk_data(chunk.raw)
            chunk.raw = len(decrypted_data).to_bytes(4, "big") + bytearray(chunk.raw[4:8]) + decrypted_data + bytearray(chunk.raw[-4:])
            chunk.update_crc()

    def _encrypt_chunk_data(self, raw_chunk):
        beg_idx, end_idx = 0, self._rsa.num_bytes - ElectronicCodeBook.padding_len
        result = bytearray()
        chunk_data = raw_chunk[8:-4]
        while beg_idx < len(chunk_data):
            result += ElectronicCodeBook.encrypt(self._rsa, chunk_data[beg_idx: end_idx])
            beg_idx = end_idx
            end_idx += self._rsa.num_bytes - ElectronicCodeBook.padding_len
        return result

    def _decrypt_chunk_data(self, raw_chunk):
        beg_idx, end_idx = 0, self._rsa.num_bytes
        result = bytearray()
        chunk_data = raw_chunk[8:-4]
        while beg_idx < len(chunk_data):
            result += ElectronicCodeBook.decrypt(self._rsa, chunk_data[beg_idx: end_idx])
            beg_idx = end_idx
            end_idx += self._rsa.num_bytes
        return result
