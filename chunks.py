import zlib
from PIL.ExifTags import TAGS
import struct


class Chunk:
    # compression methods, only one possible
    compression_method = {
        0: "DEFLATE",
    }
    # filter methods, only one possible
    filter_method = {
        0: "Adaptive",
    }
    # for IHDR chunk color type
    color_types = {
        0: "grayscale",
        2: "true color",
        3: "indexed color",
        4: "grayscale with alpha",
        6: "true color with alpha"
    }
    # descriptions for specific chunks
    chunks_description = {
        "IHDR": "image header",
        "PLTE": "palette: a list of colors",
        "IDAT": "image data",
        "IEND": "end of file",
        "sBIT": "significant bits: color-accuracy of the source data",
        "gAMA": "image gamma",
        "sRGB": "standard RGB colour space",
        "pHYs": "physical pixel dimensions",
        "tEXt": "textual data",
        "iTXt": "international textual data",
        "zTXt": "compressed textual data",
        "iCCP": "embedded ICC profile",
        "tIME": "last modification time",
        "bKGD": "background colour",
        "cHRM": "primary chromaticities and white point",
        "hIST": "image histogram",
        "sPLT": "suggested palette",
        "eXIf": "exif data"
    }
    # for sRGB chunk rendering intent
    standard_rgb = {
        0: "Perceptual",
        1: "Relative colorimetric",
        2: "Saturation",
        3: "Absolute colorimetric"
    }

    def __init__(self, chunk: list[int]):
        self.raw = chunk
        self.length = int.from_bytes(chunk[0:4], byteorder="big")
        self.name = "".join([chr(c) for c in chunk[4:8]])
        data_end_idx = self.length + 8
        self.data = {"raw": chunk[8:data_end_idx]}
        self.crc = chunk[data_end_idx:data_end_idx + 4]

        if self.name == "IHDR":
            self._parse_ihdr_data()
        elif self.name == "PLTE":
            self._parse_plte_data()
        elif self.name == "sBIT":
            self._parse_sbit_data()
        elif self.name == "gAMA":
            self._parse_gama_data()
        elif self.name == "sRGB":
            self._parse_srgb_data()
        elif self.name == "pHYs":
            self._parse_phys_data()
        elif self.name == "tEXt":
            self._parse_text_data()
        elif self.name == "zTXt":
            self._parse_ztxt_data()
        elif self.name == "iCCP":
            self._parse_iccp_data()
        elif self.name == "iTXt":
            self._parse_itxt_data()
        elif self.name == "tIME":
            self._parse_time_data()
        elif self.name == "bKGD":
            self._parse_bkgd_data()
        elif self.name == "cHRM":
            self._parse_chrm_data()
        elif self.name == "hIST":
            self._parse_hist_data()
        elif self.name == "sPLT":
            self._parse_splt_data()
        elif self.name == "eXIf":
            self._parse_exif_data()

    def display(self, hide_raw_data=True):
        print(self.to_sting(hide_raw_data=hide_raw_data))

    def to_sting(self, hide_raw_data=True):
        description = Chunk.chunks_description[self.name] if self.name in Chunk.chunks_description.keys() else ""
        result = f"Chunk: {self.name}  ({description})\n\tlength: {self.length}\n\tdata:\n"
        for key, value in self.data.items():
            if hide_raw_data and key == "raw":
                continue
            result += f"\t\t{key}: {value}\n"
        result += f"\tcrc: {self.crc}\n"
        return result

    def _parse_ihdr_data(self):
        raw_data = self.data["raw"]
        self.data["width"] = int.from_bytes(raw_data[0:4], byteorder="big")
        self.data["height"] = int.from_bytes(raw_data[4:8], byteorder="big")
        self.data["bit_depth"] = int.from_bytes(raw_data[8:9], byteorder="big")
        self.data["color_type"] = Chunk.color_types[int.from_bytes(raw_data[9:10], byteorder="big")]
        self.data["compression_method"] = Chunk.compression_method[int.from_bytes(raw_data[10:11], byteorder="big")]
        self.data["filter_method"] = Chunk.filter_method[int.from_bytes(raw_data[11:12], byteorder="big")]
        self.data["interlace_method"] = "Adam7" if int.from_bytes(raw_data[12:13], byteorder="big") == 1 else "none"

    def _parse_plte_data(self):
        self.data["number of entries"] = self.length // 3

    def _parse_sbit_data(self):
        raw_data = self.data["raw"]
        if self.length in [1, 2]:
            self.data["gray"] = int.from_bytes(raw_data[0:1], byteorder="big")
        elif self.length in [3, 4]:
            self.data["red"] = int.from_bytes(raw_data[0:1], byteorder="big")
            self.data["green"] = int.from_bytes(raw_data[1:2], byteorder="big")
            self.data["blue"] = int.from_bytes(raw_data[2:3], byteorder="big")
        if self.length == 2:
            self.data["alpha"] = int.from_bytes(raw_data[1:2], byteorder="big")
        if self.length == 4:
            self.data["alpha"] = int.from_bytes(raw_data[3:4], byteorder="big")

    def _parse_gama_data(self):
        raw_data = self.data["raw"]
        self.data["gamma"] = int.from_bytes(raw_data[0:4], byteorder="big") / 100000

    def _parse_srgb_data(self):
        raw_data = self.data["raw"]
        self.data["rendering_intent"] = Chunk.standard_rgb[int.from_bytes(raw_data[0:1], byteorder="big")]

    def _parse_phys_data(self):
        raw_data = self.data["raw"]
        self.data["horizontal_resolution (pixels per unit)"] = int.from_bytes(raw_data[0:4], byteorder="big")
        self.data["vertical_resolution (pixels per unit)"] = int.from_bytes(raw_data[4:8], byteorder="big")
        self.data["unit"] = "meter" if int.from_bytes(raw_data[8:9], byteorder="big") == 1 else "unknown"

    @staticmethod
    def _get_text(data: list[int]) -> tuple:
        idx = 0
        for idx, byte in enumerate(data):
            if chr(byte) == '\0':
                idx += 1
                break
        text = bytearray(data[0:idx - 1]).decode("utf-8", "ignore")
        return text, idx

    def _parse_text_data(self):
        raw_data = self.data["raw"]
        keyword, idx = self._get_text(raw_data)
        self.data["keyword"] = keyword
        text, _ = self._get_text(raw_data[idx:])
        self.data["text"] = text

    def _parse_compressed_text_chunk(self, decode=True):
        raw_data = self.data["raw"]
        keyword, idx = self._get_text(raw_data)
        self.data["keyword"] = keyword
        self.data["compression_method"] = Chunk.compression_method[int.from_bytes(raw_data[idx:idx + 1], byteorder="big")]
        if decode:
            self.data["text"] = zlib.decompress(bytearray(raw_data[idx + 1:])).decode("utf-8", "ignore")
        else:
            self.data["text"] = zlib.decompress(bytearray(raw_data[idx + 1:]))

    def _parse_ztxt_data(self):
        self._parse_compressed_text_chunk()

    def _parse_iccp_data(self):
        self._parse_compressed_text_chunk(decode=False)

    def _parse_itxt_data(self):
        raw_data = self.data["raw"]
        keyword, idx = self._get_text(raw_data)
        self.data["keyword"] = keyword
        self.data["compression_flag"] = int.from_bytes(raw_data[idx:idx + 1], byteorder="big")
        self.data["compression_method"] = Chunk.compression_method[
            int.from_bytes(raw_data[idx + 1:idx + 2], byteorder="big")]
        offset = idx + 2
        language_tag, idx = self._get_text(raw_data[idx + 2:])
        idx += offset
        self.data["language_tag"] = language_tag
        offset = idx
        translated_keyword, idx = self._get_text(raw_data[idx:])
        idx += offset
        self.data["translated_keyword"] = translated_keyword
        if self.data["compression_flag"] == 0:
            self.data["text"] = bytearray(raw_data[idx:]).decode("utf-8", "ignore")
        else:
            self.data["text"] = zlib.decompress(bytearray(raw_data[idx + 1:])).decode("utf-8", "ignore")

    def _parse_time_data(self):
        raw_data = self.data["raw"]
        self.data["year"] = int.from_bytes(raw_data[0:2], byteorder="big")
        self.data["month"] = int.from_bytes(raw_data[2:3], byteorder="big")
        self.data["day"] = int.from_bytes(raw_data[3:4], byteorder="big")
        self.data["hour"] = int.from_bytes(raw_data[4:5], byteorder="big")
        self.data["minute"] = int.from_bytes(raw_data[5:6], byteorder="big")
        self.data["second"] = int.from_bytes(raw_data[6:7], byteorder="big")

    def _parse_bkgd_data(self):
        raw_data = self.data["raw"]
        # grayscale
        if self.length == 2:
            self.data["gray"] = int.from_bytes(raw_data[0:2], byteorder="big")
        # color
        elif self.length == 6:
            self.data["red"] = int.from_bytes(raw_data[0:2], byteorder="big")
            self.data["green"] = int.from_bytes(raw_data[2:4], byteorder="big")
            self.data["blue"] = int.from_bytes(raw_data[4:6], byteorder="big")
        # index color
        elif self.length == 1:
            self.data["palette_index"] = int.from_bytes(raw_data[0:1], byteorder="big")

    def _parse_chrm_data(self):
        raw_data = self.data["raw"]
        self.data["white_point_x"] = int.from_bytes(raw_data[0:4], byteorder="big") / 100000
        self.data["white_point_y"] = int.from_bytes(raw_data[4:8], byteorder="big") / 100000
        self.data["red_x"] = int.from_bytes(raw_data[8:12], byteorder="big") / 100000
        self.data["red_y"] = int.from_bytes(raw_data[12:16], byteorder="big") / 100000
        self.data["green_x"] = int.from_bytes(raw_data[16:20], byteorder="big") / 100000
        self.data["green_y"] = int.from_bytes(raw_data[20:24], byteorder="big") / 100000
        self.data["blue_x"] = int.from_bytes(raw_data[24:28], byteorder="big") / 100000
        self.data["blue_y"] = int.from_bytes(raw_data[28:32], byteorder="big") / 100000

    def _parse_hist_data(self):
        raw_data = self.data["raw"]
        hist = []
        for i in range(0, self.length, 2):
            hist.append(int.from_bytes(raw_data[i:i+2], byteorder="big"))
        self.data["histogram"] = hist

    def _parse_splt_data(self):
        raw_data = self.data["raw"]
        name, idx = self._get_text(raw_data)
        self.data["palette name"] = name
        self.data["sample depth"] = int.from_bytes(raw_data[idx:idx + 1], byteorder="big")
        entries_len = self.length - idx - 1
        self.data["number of entries"] = entries_len // 10 if self.data["sample depth"] == 16 else entries_len // 6

    def _parse_exif_data(self):
        raw_data = self.data["raw"]
        order_code = f"{chr(raw_data[0])}{chr(raw_data[1])}"

        if order_code == "MM":
            byteorder = "big"
        elif order_code == "II":
            byteorder = "little"
        else:
            self.data["error"] = "header: invalid byteorder"
            return

        if int.from_bytes(raw_data[2:4], byteorder=byteorder) != 42:
            self.data["error"] = "header: not a tiff"
            return

        offset = int.from_bytes(raw_data[4:8], byteorder=byteorder)
        while offset != 0:
            offset = self._parse_ifd(raw_data, offset, byteorder)

    def _parse_ifd(self, data, offset, byteorder):
        number_of_entries = int.from_bytes(data[offset: offset + 2], byteorder=byteorder)
        offset += 2

        for _ in range(number_of_entries):
            tag_id = int.from_bytes(data[offset: offset + 2], byteorder=byteorder)
            offset += 2
            tag = TAGS[tag_id] if tag_id in TAGS.keys() else f"unknown tag: {hex(tag_id)}"
            tag_type = int.from_bytes(data[offset: offset + 2], byteorder=byteorder)
            offset += 2
            count = int.from_bytes(data[offset: offset + 4], byteorder=byteorder)
            offset += 4
            data_value = int.from_bytes(data[offset: offset + 4], byteorder=byteorder)

            # unsigned byte
            if tag_type == 1:
                if byteorder == "big":
                    decoded_data = int.from_bytes(data[offset: offset + 1], byteorder=byteorder)
                else:
                    decoded_data = int.from_bytes(data[offset + 3: offset + 4], byteorder=byteorder)
            # ascii string
            elif tag_type == 2:
                if count <= 4:
                    decoded_data = data_value.to_bytes(byteorder=byteorder, length=4).decode("ascii")
                else:
                    decoded_data = "".join(chr(c) for c in data[data_value: data_value + count - 1])
            # unsigned short
            elif tag_type == 3:
                if byteorder == "big":
                    decoded_data = int.from_bytes(data[offset: offset + 2], byteorder=byteorder)
                else:
                    decoded_data = int.from_bytes(data[offset + 2: offset + 4], byteorder=byteorder)
            # unsigned long
            elif tag_type == 4:
                decoded_data = int.from_bytes(data[offset: offset + 4], byteorder=byteorder)
            # unsigned rational (fractal)
            elif tag_type == 5:
                numerator = int.from_bytes(data[data_value: data_value + 4], byteorder=byteorder)
                denominator = int.from_bytes(data[data_value + 4: data_value + 8], byteorder=byteorder)
                decoded_data = numerator / denominator
            # signed byte / signed short / signed long
            elif tag_type == 6:
                if byteorder == "big":
                    decoded_data = int.from_bytes(data[offset: offset + 1], byteorder=byteorder, signed=True)
                else:
                    decoded_data = int.from_bytes(data[offset + 3: offset + 4], byteorder=byteorder, signed=True)
            # signed short
            elif tag_type == 8:
                if byteorder == "big":
                    decoded_data = int.from_bytes(data[offset: offset + 2], byteorder=byteorder, signed=True)
                else:
                    decoded_data = int.from_bytes(data[offset + 2: offset + 4], byteorder=byteorder, signed=True)
            # signed long
            elif tag_type == 9:
                decoded_data = int.from_bytes(data[offset: offset + 4], byteorder=byteorder, signed=True)
            # signed rational
            elif tag_type == 10:
                numerator = int.from_bytes(data[data_value: data_value + 4], byteorder=byteorder, signed=True)
                denominator = int.from_bytes(data[data_value + 4: data_value + 8], byteorder=byteorder, signed=True)
                decoded_data = numerator / denominator
            # single float
            elif tag_type == 11:
                decoded_data = struct.unpack("f", data[offset: offset + 4])
            # double float
            elif tag_type == 12:
                decoded_data = struct.unpack("f", data[data_value: data_value + 8])
            # undefined / other
            else:
                decoded_data = f"undefined format value: {tag_type}"

            self.data[tag] = decoded_data
            # skip data value
            offset += 4

        next_ifd_offset = int.from_bytes(data[offset: offset + 4], byteorder=byteorder)
        return next_ifd_offset  # if next_ifd_offset != 0 else "end"
