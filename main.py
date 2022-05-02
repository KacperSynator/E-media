from png_image import PNGImage


def main():
    png_im = PNGImage("data/.png")
    png_im.display_data()
    # png_im.display_image()
    # png_im.fft()
    # png_im.anonymize("data/out.png")


if __name__ == '__main__':
    main()
