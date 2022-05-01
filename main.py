from png_image import PNGImage


def main():
    png_im = PNGImage("data/8-bit-256-x-256-Grayscale-Lena-Image.png")
    png_im.display_data()
    png_im.display_image()
    png_im.fft()


if __name__ == '__main__':
    main()
