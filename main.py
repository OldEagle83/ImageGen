import os

import nltk
import random
import re
import downloader
import logging
import manipulation
from nltk import WordNetLemmatizer
# import messages  # Todo: add messages for console input menu

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
        self.get_quote()

    def get_quote(self):
        # Get a random quote from quotes.txt
        with open('quotes.txt', 'r') as f:
            quotes = f.readlines()

        self.prep_text(random.choice(quotes))

        return self.text, self.author

    def prep_text(self, text):
        # Separates a text of form quote -Author and breaks it down to parts of speech

        self.author = [match.group(1) for match in re.finditer(r'[—―]([ .A-Za-z]+)', text)][0]
        self.text = [match.group(1) for match in re.finditer(r'(.+) *[—―]', text)][0].strip().replace('"', '')

        self.nouns = self.get_pos('NN')
        self.verbs = self.get_pos('VB')
        self.adjectives = self.get_pos('JJ')

    def get_pos(self, pos):
        # Returns a list with the words that are of the given part of speech
        is_pos = lambda part: part[:2] == pos
        tokenized = nltk.wordpunct_tokenize(self.text)
        results = [word for (word, pos) in nltk.pos_tag(tokenized) if is_pos(pos)]
        if pos == 'VB':
            results = [WordNetLemmatizer().lemmatize(word, 'v') for word in results]
        results = sorted([x for x in results if len(x) > 1 and x.lower() not in self.banned], key=len, reverse=True)
        logging.debug(f'{pos}: {results}')
        return results


quote = Quote()
logging.info(f'Selected: {quote.text} by {quote.author}')
# print(quote.text, quote.author, quote.nouns, quote.verbs)
if quote.nouns:
    if quote.verbs:
        img_folder = downloader.download(quote.nouns[0] + ' ' + quote.verbs[0], 3)
    else:
        img_folder = downloader.download(quote.nouns[0], 3)

image = manipulation.Img(img_folder + '/' + random.choice(os.listdir(img_folder)), text=quote.text, author=quote.author)
image.draw()

if __name__ == '__main__':
    pass  # TODO: Add console menu