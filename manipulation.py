from PIL import Image, ImageFilter, ImageFont, ImageDraw
import textwrap

class Img:
    def __init__(self, path, text, author):
        self.image = Image.open(path)
        self.width, self.height = self.image.size
        self.text = text
        self.author = author if author else ""

    def blur(self, amount: int):
        return self.image.filter(ImageFilter.GaussianBlur(amount))

    def draw(self):
        text_size = int(self.width/33)

        # Set up fonts
        font = ImageFont.truetype('fonts/SpecialElite-Regular.ttf', text_size)
        author_font = ImageFont.truetype('fonts/Quicksand-VariableFont_wght.ttf', int(text_size/2))

        # Blur the image and prepare text
        blurred_img = self.blur(20)
        image_editable = ImageDraw.Draw(blurred_img)
        lines = textwrap.wrap(self.text, width=45) + [self.author]

        # Set the height for the first line
        rolling_height = self.height/2 - (text_size * (int(len(lines)/2) + 1))

        for i, line in enumerate(lines):

            # The last line is the author
            if i == len(lines) - 1:
                width = author_font.getlength(line)
                rolling_height += text_size * 2
                image_editable.text((self.width - (self.width - width) / 2 - width, rolling_height), line, font=author_font)
                break

            width = font.getlength(line)
            rolling_height += text_size + int(text_size * 15/100)
            image_editable.text((self.width - (self.width - width)/2 - width, rolling_height), line, font=font)

        blurred_img.show()


# draw('img/empty_roads/MnwxMjA3fDB8MXxzZWFyY2h8M3x8ZHJvbmUlMjBzaG90c3xlbnwwfDB8fHwxNjY2NDg1NjQ1.jpg', "The hard days are what make you stronger.")

if __name__ == '__main__':
    image = Img('img/empty_roads/MnwxMjA3fDB8MXxzZWFyY2h8M3x8ZHJvbmUlMjBzaG90c3xlbnwwfDB8fHwxNjY2NDg1NjQ1.jpg', 'One liner to test height', 'John Geroitos')
    image.draw()