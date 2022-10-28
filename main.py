import math
import os
import string

import nltk
import random
import re
import downloader
import logging
from nltk import WordNetLemmatizer
import textwrap
from PIL import ImageDraw, ImageFont, ImageStat, ImageFilter
import messages



# Comment these out after first run
# nltk.download('averaged_perceptron_tagger')
# nltk.download('omw-1.4')
# nltk.download('wordnet')

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')


class Quote:
    def __init__(self, text=None, author=None):
        self.text = text
        self.author = author
        self.tokenized = []
        self.nouns = []
        self.verbs = []
        self.adjectives = []
        self.search_str = ''
        self.banned = ['person', 'face']
        self.font_color = (255, 255, 255, 255)

        if not self.text:
            self.get_quote()

        else:
            self.build_search_str()

        self.font = None
        self.author_font = None

    def get_quote(self):
        # Get a random quote from quotes.txt
        with open('quotes.txt', 'r') as f:
            quotes = f.readlines()

        text = random.choice(quotes)
        self.author = [match.group(1) for match in re.finditer(r'[—―]([ .A-Za-z]+)', text)][0]
        self.text = [match.group(1) for match in re.finditer(r'(.+) *[—―]', text)][0].strip().replace('"', '')
        self.build_search_str()

    def build_search_str(self):
        # Breaks down sentence to parts of speech (NN: Nouns, VB: Verbs, JJ: Adjectives) and forms a search string
        self.tokenized = nltk.wordpunct_tokenize(self.text)
        self.nouns = self.get_pos('NN')
        self.verbs = self.get_pos('VB')
        self.adjectives = self.get_pos('JJ')
        phrase = self.nouns[0] if self.nouns else ''
        phrase += ' ' + self.adjectives[0] \
            if self.adjectives \
            else ' ' + self.verbs[0] \
            if self.verbs \
            else ''

        self.search_str = phrase

    def nametize(self):
        result = ''
        for i, char in enumerate(self.search_str.lower()):
            if char in string.ascii_lowercase:
                result += char
            elif char == ' ' and 0 < i < len(self.search_str) - 1:
                result += '_'
        return result

    def get_pos(self, pos: str) -> list:
        """
        # Returns a list with the words that are of the given part of speech
        :param pos: acceptable values ['VB', 'JJ', 'NN']
        :return: Lemmatized words in a list
        """
        is_pos = lambda part: part[:2] == pos

        results = [word for (word, pos) in nltk.pos_tag(self.tokenized) if is_pos(pos)]
        if pos == 'VB':
            results = [WordNetLemmatizer().lemmatize(word, 'v') for word in results]
        results = sorted([x for x in results if len(x) > 1 and x.lower() not in self.banned], key=len, reverse=True)
        logging.info(f'{pos}: {results}')
        return results


class Img:
    def __init__(self, image):
        self.image = image
        self.width, self.height = self.image.size
        self.bright = self.brightness()

    def brightness(self):
        # Returns the median brightness of the center of image
        img_copy = self.image.copy()
        center_rect = img_copy.crop((int(self.width * 20 / 100), int(self.height * 40 / 100),
                                     self.width - int(self.width * 20 / 100), self.height - int(self.height * 40 / 100)))
        stat = ImageStat.Stat(center_rect)
        r, g, b = stat.mean
        return math.sqrt(0.241 * (r ** 2) + 0.691 * (g ** 2) + 0.068 * (b ** 2))

    def blur(self, amount: int):
        return self.image.filter(ImageFilter.GaussianBlur(amount))


class InspiringImg:
    def __init__(self, quote=None, orientation=None, color=None):
        if not quote:
            self.quote = Quote()
        else:
            self.quote = quote

        self.gen = downloader.img_gen(self.quote.search_str, orientation=orientation, color=color)
        self.src_img = Img(next(self.gen))
        self.quote.font = ImageFont.truetype('fonts/SpecialElite-Regular.ttf', int(self.src_img.width / 33))
        self.quote.author_font = ImageFont.truetype('fonts/Quicksand-VariableFont_wght.ttf', int((self.src_img.width / 33) / 2))

        if self.src_img.bright < 80:
            self.quote.font_color = (255, 255, 255, 255)

        else:
            self.quote.font_color = (0, 0, 0, 0)

        self.image = None
        self.quote_changed = False

    def new_img(self):
        if self.quote_changed:
            self.gen = downloader.img_gen(self.quote.search_str)
        self.src_img = Img(next(self.gen))
        self.quote.font = ImageFont.truetype('fonts/SpecialElite-Regular.ttf', int(self.src_img.width / 33))
        self.quote.author_font = ImageFont.truetype('fonts/Quicksand-VariableFont_wght.ttf', int((self.src_img.width / 33) / 2))

    def toggle_font_color(self):
        if self.quote.font_color == (255, 255, 255, 255):
            self.quote.font_color = (0, 0, 0, 0)
        else:
            self.quote.font_color = (255, 255, 255, 255)

    def new_quote(self):
        self.quote = Quote()
        self.quote.font = ImageFont.truetype('fonts/SpecialElite-Regular.ttf', int(self.src_img.width / 33))
        self.quote.author_font = ImageFont.truetype('fonts/Quicksand-VariableFont_wght.ttf', int((self.src_img.width / 33) / 2))
        self.quote_changed = True

    def save_file(self):

        # Check if director img/ exists, create it if not
        if not os.path.isdir('img'):
            os.mkdir('img')
        f_name = self.quote.nametize()
        counter = 1

        # Check if target filename exists, append _1, 2, 3 if it does
        while os.path.isfile(f'img/{f_name}.jpg'):
            f_name += f'_{str(counter)}'
            counter += 1

        # Save file to img/ directory
        self.image.save(f'img/{f_name}.jpg')
        print(messages.success_save)

    def draw(self):
        # Draw the selected quote on the image. Wrap quote, decide font color based on
        # perceived brightness and show it
        print(f'Perceived image brightness: {self.src_img.bright}')

        # Blur the image and prepare text
        self.image = self.src_img.blur(20)
        image_editable = ImageDraw.Draw(self.image)
        lines = textwrap.wrap(self.quote.text, width=45) + [self.quote.author]

        # Set the height for the first line
        y = self.src_img.height / 2 - (self.quote.font.size * (int(len(lines) / 2) + 1))

        max_width = 0

        # Check image brightness, set font color to black if image is too bright

        for i, line in enumerate(lines):

            # The last line is the author
            if i == len(lines) - 1:
                author_width = self.quote.author_font.getlength(line)
                y += self.quote.font.size * 2
                image_editable.text((self.src_img.width - author_width - max_width * 0.3, y),
                                    '—' + line, font=self.quote.author_font, fill=self.quote.font_color)
                break

            width = self.quote.font.getlength(line)
            max_width = width if max_width < width else max_width
            y += self.quote.font.size + int(self.quote.font.size * 15/100)
            x = self.src_img.width - (self.src_img.width - width) / 2 - width

            # Draw text over the outline
            image_editable.text((x, y), line, font=self.quote.font, fill=self.quote.font_color)

        return self.image


def ask_orientation():
    orientation = input(messages.enter_or)
    if orientation.lower() in ['l', 'p', 's']:
        orientation = {'l': 'landscape', 'p': 'portrait', 's': 'squarish'}[orientation.lower()]
    else:
        orientation = None
    return orientation


def ask_color():
    colors = ['black', 'white', 'yellow', 'orange', 'red', 'blue', 'green' 'purple', 'magenta', 'teal']
    color = input(messages.enter_color)
    if color.lower() in colors:
        return color.lower()
    return None


def menu():
    while True:
        print(messages.welcome)
        print(messages.main_menu)
        selection = input()
        if selection.isnumeric():
            if int(selection) == 1:
                quote = Quote()

            elif int(selection) == 2:
                quote_text = input(messages.enter_quote)
                quote_author = input(messages.enter_author)
                quote = Quote(text=quote_text, author=quote_author)

            else:
                break
            img = InspiringImg(quote)
            img.draw().show()
            while True:
                print(messages.img_menu)
                selection = input()
                if selection.isnumeric():

                    if int(selection) == 1:
                        img.save_file()
                        break

                    elif int(selection) == 2:
                        img.new_img()

                    elif int(selection) == 3:
                        img.new_quote()

                    elif int(selection) == 4:
                        img.toggle_font_color()

                    else:
                        break

                    img.draw().show()
        else:
            break


if __name__ == '__main__':
    menu()



