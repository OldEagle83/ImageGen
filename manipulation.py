from PIL import Image, ImageFilter, ImageFont, ImageDraw, ImageStat
import math
import textwrap

import downloader
import main
import logging  # Add logging


class Img:
    def __init__(self, img: bytes, quote, orientation='landscape'):
        self.image = Image.open(img)
        self.width, self.height = self.image.size
        self.text = quote.text
        self.author = quote.author if quote.author else ''
        self.orientation = orientation
        self.bright = self.brightness()

    def brightness(self):
        # Returns the median brightness of the image

        stat = ImageStat.Stat(self.image)
        r, g, b = stat.mean
        return math.sqrt(0.241 * (r ** 2) + 0.691 * (g ** 2) + 0.068 * (b ** 2))

    def blur(self, amount: int):
        return self.image.filter(ImageFilter.GaussianBlur(amount))

    def draw(self):
        # Draw the selected quote on the image. Wrap quote, decide font color based on
        # perceived brightness and show it
        text_size = int(self.width/33)
        print(f'Perceived image brightness: {self.bright}')

        # Set up fonts
        font = ImageFont.truetype('fonts/SpecialElite-Regular.ttf', text_size)
        author_font = ImageFont.truetype('fonts/Quicksand-VariableFont_wght.ttf', int(text_size/2))

        # Blur the image and prepare text
        blurred_img = self.blur(20)
        image_editable = ImageDraw.Draw(blurred_img)
        lines = textwrap.wrap(self.text, width=45) + [self.author]

        # Set the height for the first line
        y = self.height/2 - (text_size * (int(len(lines)/2) + 1))

        max_width = 0

        # Check image brightness, set font color to black if image is too bright
        if self.bright < 100:
            font_color = (255, 255, 255, 255)
            outline_color = (225, 225, 225, 1)

        else:
            font_color = (0, 0, 0, 0)
            outline_color = (30, 30, 30, 1)

        for i, line in enumerate(lines):

            # The last line is the author
            if i == len(lines) - 1:
                author_width = author_font.getlength(line)
                y += text_size * 2
                image_editable.text((self.width - author_width - max_width * 0.3, y),
                                    '—' + line, font=author_font, fill=font_color)
                break

            width = font.getlength(line)
            max_width = width if max_width < width else max_width
            y += text_size + int(text_size * 15/100)
            x = self.width - (self.width - width)/2 - width

            # Draw outline of text
            image_editable.text((x - 1, y), line, font=font, fill=outline_color)
            image_editable.text((x + 1, y), line, font=font, fill=outline_color)
            image_editable.text((x, y - 1), line, font=font, fill=outline_color)
            image_editable.text((x, y + 1), line, font=font, fill=outline_color)

            # Draw text over the outline
            image_editable.text((x, y), line, font=font, fill=font_color)


        blurred_img.show()
        return blurred_img


if __name__ == '__main__':
    quote = main.Quote()
    gen = downloader.img_gen(quote.search_str)
    image = Img(next(gen), quote)
    image.draw()
