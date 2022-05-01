class Chunk:
    # for IHDR chunk color type
    color_types = {
        0: "grayscale",
        2: "true color",
        3: "indexed color",
        4: "grayscale with alpha",
        6: "true color with alpha"
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

    def display(self, hide_raw_data=True):
        print(f"Chunk: {self.name}\n\tlength: {self.length}\n\tdata:")
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
        self.data["compression_method"] = int.from_bytes(raw_data[10:11], byteorder="big")
        self.data["filter method"] = int.from_bytes(raw_data[11:12], byteorder="big")
        self.data["interlace_method"] = "Adam7" if int.from_bytes(raw_data[12:13], byteorder="big") == 1 else "none"


