import zlib

from PIL import Image, ImageFile
import numpy as np
from chunks import Chunk
from rsa import MyRSA
from block_cipher import ElectronicCodeBook, Counter
from multiprocessing import Pool
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

    def join_idat_chunks(self):
        idats = list(filter(lambda chunk: chunk.name == "IDAT", self.chunks))
        if len(idats) == 1:
            return
        new_idat_data, new_idat_len = bytearray(idats[0].raw[8:-4]), idats[0].length
        for idat in idats[1:]:
            new_idat_len += idat.length
            new_idat_data += bytearray(idat.raw[8:-4])
            self.chunks.remove(idat)
        idats[0].raw = bytearray(new_idat_len.to_bytes(4, "big")) + bytearray("IDAT".encode("ascii")) + new_idat_data + bytearray("chuj".encode("ascii"))
        idats[0].length = new_idat_len

    def encrypt(self, number_of_bits):
        if not self._rsa:
            self._rsa = MyRSA(number_of_bits)
        self.join_idat_chunks()
        idat_chunks = tuple(filter(lambda chunk_: chunk_.name == "IDAT", self.chunks))
        with Pool() as pool:
            res = pool.map(self._encrypt_chunk_data, idat_chunks)
        for chunk, new in zip(idat_chunks, res):
            chunk.raw = new

    def decrypt(self, number_of_bits):
        if not self._rsa:
            self._rsa = MyRSA(number_of_bits)
        idat_chunks = list(filter(lambda chunk_: chunk_.name == "IDAT", self.chunks))
        with Pool() as pool:
            res = pool.map(self._decrypt_chunk_data, idat_chunks)
        for chunk, new in zip(idat_chunks, res):
            chunk.raw = new

    def _encrypt_chunk_data(self, chunk):
        chunk.decompress_data()
        result = ElectronicCodeBook.encrypt(self._rsa, chunk.raw[8:-4])
        compressed_result = bytearray(zlib.compress(result))
        compressed_result1 = bytearray(zlib.compress(result[:chunk.length])[2:-4])
        compressed_result2 = bytearray(zlib.compress(result[chunk.length:])[2:-4])
        print(chunk.length)
        print(len(result))
        print(len(compressed_result))
        chunk.length = len(compressed_result)
        chunk.raw = bytearray(chunk.length.to_bytes(4, "big")) + bytearray(chunk.raw[4:8]) + compressed_result[:chunk.length] + bytearray(chunk.raw[-4:])
        # chunk.raw = zlib.compress(result, 8)[2:-4]
        # chunk.raw = bytearray(len(compressed_result1).to_bytes(4, "big")) + bytearray(chunk.raw[4:8]) + compressed_result1 + bytearray( chunk.raw[-4:])
        # text_chunk = bytearray((len(compressed_result) - chunk.length).to_bytes(4, "big")) + bytearray("tEXt".encode("ascii")) + compressed_result[chunk.length:] + bytearray(chunk.raw[-4:])
        return chunk.raw #+ text_chunk

    def _decrypt_chunk_data(self, chunk):
        result = ElectronicCodeBook.decrypt(self._rsa, chunk.raw[8:-4])
        chunk.raw = len(result).to_bytes(4, "big") + bytearray(chunk.raw[4:8]) + result + bytearray(chunk.raw[-4:])
        chunk.update_crc()
        return chunk.raw
