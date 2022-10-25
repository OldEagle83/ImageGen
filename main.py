import os

import nltk
import random
import re
import downloader
import logging
import manipulation
from nltk import WordNetLemmatizer
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
        self.nouns = []
        self.verbs = []
        self.adjectives = []
        self.banned = ['person', 'face']
        if not self.text:
            self.get_quote()
        else:
            self.build_pos()


    def get_quote(self) -> tuple:
        # Get a random quote from quotes.txt
        with open('quotes.txt', 'r') as f:
            quotes = f.readlines()

        self.prep_text(random.choice(quotes))

        return self.text, self.author

    def prep_text(self, text: str):
        # Separates a text of form quote -Author and breaks it down to parts of speech

        self.author = [match.group(1) for match in re.finditer(r'[—―]([ .A-Za-z]+)', text)][0]
        self.text = [match.group(1) for match in re.finditer(r'(.+) *[—―]', text)][0].strip().replace('"', '')
        self.build_pos()

    def build_pos(self):
        self.nouns = self.get_pos('NN')
        self.verbs = self.get_pos('VB')
        self.adjectives = self.get_pos('JJ')

    def get_pos(self, pos: str) -> list:
        """
        # Returns a list with the words that are of the given part of speech
        :param pos: acceptable values ['VB', 'JJ', 'NN']
        :return: Lemmatized words in a list
        """
        is_pos = lambda part: part[:2] == pos
        tokenized = nltk.wordpunct_tokenize(self.text)
        results = [word for (word, pos) in nltk.pos_tag(tokenized) if is_pos(pos)]
        if pos == 'VB':
            results = [WordNetLemmatizer().lemmatize(word, 'v') for word in results]
        results = sorted([x for x in results if len(x) > 1 and x.lower() not in self.banned], key=len, reverse=True)
        logging.debug(f'{pos}: {results}')
        return results


def start(text=None, author=None, orientation=None):
    if not text:
        quote = Quote()
    else:
        quote = Quote(text, author)

    logging.info(f'Selected: {quote.text} by {quote.author}')
    if quote.nouns:
        if quote.verbs:
            img_folder = downloader.download(quote.nouns[0] + ' ' + quote.verbs[0], 8,
                                             orientation=orientation)
        else:
            img_folder = downloader.download(quote.nouns[0], 8, orientation=orientation)

    image = manipulation.Img(img_folder + '/' + random.choice(os.listdir(img_folder)), text=quote.text,
                             author=quote.author)
    image.draw()

def ask_orientation():
    orientation = input(messages.enter_or)
    if orientation.lower() in ['l', 'p', 's']:
        orientation = {'l': 'landscape', 'p': 'portrait', 's': 'squarish'}[orientation.lower()]
    else:
        orientation = None
    return orientation

def menu():
    while True:
        print(messages.welcome)
        print(messages.main_menu)
        selection = input()
        if selection == '1':
            start(orientation=ask_orientation())
        elif selection == '2':
            quote_text = input(messages.enter_quote)
            quote_author = input(messages.enter_author)
            start(text=quote_text, author=quote_author, orientation=ask_orientation())
        else:
            break

if __name__ == '__main__':
    menu()

