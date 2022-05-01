from png_image import PNGImage


def main():
    png_im = PNGImage("data/dices.png")
    png_im.display_data()
    png_im.display_image()


if __name__ == '__main__':
    main()
