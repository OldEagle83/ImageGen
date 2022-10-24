import nltk
import random
import re
import img_downloader
import logging

# nltk.download('averaged_perceptron_tagger')
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
level = 'DEBUG'


class Quote():
    def __init__(self, text=None, author=None):
        self.text = text
        self.author = author


    def get_quote(self):
        # Get a random quote from quotes.txt
        with open('quotes.txt', 'r') as f:
            quotes = f.readlines()
        return quotes[random.randint(0, len(quotes))]

    def sep_author_text(self, text):
        # Separates a text of form quote -Author
        self.author = [match.group(1) for match in re.finditer(r'[—―]([ .A-Za-z]+)', text)][0]
        self.text = [match.group(1) for match in re.finditer(r'(.+) *[—―]', text)][0].strip().replace('"', '')



# def build_inspiration():
#     # Reads words from inspiring.txt and returns a lowercase list
#     with open('inspiring.txt', 'r') as f:
#         results = f.readlines()
#     return [x.lower().strip() for x in results]

def get_pos(text, pos):
    is_pos = lambda part: part[:2] == pos
    tokenized = nltk.wordpunct_tokenize(text)
    results = [word for (word, pos) in nltk.pos_tag(tokenized) if is_pos(pos)]
    return sorted([x for x in results if len(x) > 1], key=len, reverse=True)





quote = Quote()
quote.sep_author_text(quote.get_quote())
logging.info(f'Selected: {quote.text} by {quote.author}')
nouns = get_pos(quote.text, 'NN')
verbs = get_pos(quote.text, 'VB')
adjectives = get_pos(quote.text, 'JJ')
search_str = ''
search_str += nouns[0] if nouns else ''
search_str += ' ' + verbs[0] if verbs else ''
search_str += ' ' + adjectives[0] if adjectives else ''
folder = img_downloader.download(search_str)

# good_candidates = [x for x in quote.split() if x.lower() in inspirational]

