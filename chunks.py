class Chunk:
    compression_method = {
        0: "DEFLATE",
    }
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

    chunks_description = {
        "IHDR": "image header",
        "PLTE": "palette: a list of colors",
        "IDAT": "image data",
        "IEND": "end of file",
        "sBIT": "significant bits: color-accuracy of the source data",
        "gAMA": "image gamma",
        "sRGB": "standard RGB colour space",
        "pHYs": "physical pixel dimensions",
        "iTxt": "",
        "zTXt": "compressed textual data",
        "iCCP": "embedded ICC profile",
        "tIME": "last modification time",
    }

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
        elif self.name == "zTXt":
            self._parse_ztxt_data()
        elif self.name == "iCCP":
            self._parse_iccp_data()
        elif self.name == "tIME":
            self._parse_time_data()

    def display(self, hide_raw_data=True):
        description = Chunk.chunks_description[self.name] if self.name in Chunk.chunks_description.keys() else ""
        print(f"Chunk: {self.name}  ({description})\n\tlength: {self.length}\n\tdata:")
        for key, value in self.data.items():
            if hide_raw_data and key == "raw":
                continue
            print(f"\t\t{key}: {value}")
        print(f"\tcrc: {self.crc}")

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

    def _parse_compressed_text_chunk(self):
        raw_data = self.data["raw"]
        keyword = ""
        idx = 0
        for idx, byte in enumerate(raw_data):
            if chr(byte) == '\0':
                idx += 1
                break
            keyword += chr(byte)
        self.data["keyword"] = keyword
        self.data["compression method"] = Chunk.compression_method[int.from_bytes(raw_data[idx:idx + 1], byteorder="big")]

    def _parse_ztxt_data(self):
        self._parse_compressed_text_chunk()

    def _parse_iccp_data(self):
        self._parse_compressed_text_chunk()

    def _parse_time_data(self):
        raw_data = self.data["raw"]
        self.data["year"] = int.from_bytes(raw_data[0:2], byteorder="big")
        self.data["month"] = int.from_bytes(raw_data[2:3], byteorder="big")
        self.data["day"] = int.from_bytes(raw_data[3:4], byteorder="big")
        self.data["hour"] = int.from_bytes(raw_data[4:5], byteorder="big")
        self.data["minute"] = int.from_bytes(raw_data[5:6], byteorder="big")
        self.data["second"] = int.from_bytes(raw_data[6:7], byteorder="big")
