import pandas as pd
import numpy as np
import re
import unicodedata
import string
import contractions
import tensorflow as tf
import ast
import os
from num2words import num2words
from nltk.corpus import cmudict
# import copy

# import nltk
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# # from nltk.tokenize import word_tokenize
# from nltk import word_tokenize, pos_tag

_pad = "_"
_punctuation = "!'(),.:;? "
_special = "-"
_silences = ["@sp", "@spn", "@sil"]

class TextNormalizer:
    def __init__(self):
        self.abbreviations = [(re.compile('\\b%s\\.' % x[0], re.IGNORECASE), x[1]) for x in [
                ('mrs', 'misess'),
                ('mr', 'mister'),
                ('dr', 'doctor'),
                ('drs', 'doctors'),
                ('st', 'saint'),
                ('co', 'company'),
                ('jr', 'junior'),
                ('sr','senior'),
                ('maj', 'major'),
                ('gen', 'general'),
                ('drs', 'doctors'),
                ('rev', 'reverend'),
                ('lt', 'lieutenant'),
                ('hon', 'honorable'),
                ('sgt', 'sergeant'),
                ('capt', 'captain'),
                ('esq', 'esquire'),
                ('ltd', 'limited'),
                ('col', 'colonel'),
                ('ft', 'fort'),
                ('no', 'number'),
                # ('st','street'),
                ('ave','avenue'),
                # ("i.e.", "that is"),
            ]]

        # self.abbreviations = {"Mr.": "Mister",
        #                 "Mrs.": "Misses",
        #                 "Dr.": "Doctor",
        #                 "No.": "Number",
        #                 "St.": "Street",
        #                 "Co.": "Company",
        #                 "Jr.": "Junior",
        #                 "Sr.": "Senior",
        #                 "Maj.": "Major",
        #                 "Gen.": "General",
        #                 "Drs.": "Doctors",
        #                 "Rev.": "Reverend",
        #                 "Lt.": "Lieutenant",
        #                 "Hon.": "Honorable",
        #                 "Sgt.": "Sergeant",
        #                 "Capt.": "Captain",
        #                 "Esq.": "Esquire",
        #                 "Ltd.": "Limited",
        #                 "Col.": "Colonel",
        #                 "Ft.": "Fort",
        #                 "Ave.": "Avenue",
        #                 "etc.": "et cetera",
        #                 "i.e.": "that is",
        #                 "e.g.": "for example",}
        # self.special_words = {
        #                 "https": "h t t p s",
        #                 "http": "h t t p",
        #                 "gmail": "g-mail",
        #                 "yahoo": "yahoo"}

    def expand_abbreviations(self, text):
        """Expands known abbreviations in the text."""
        # for abbr, expansion in self.abbreviations.items():
        for abbr, expansion in self.abbreviations:
            # text = re.sub(r'\b'+abbr, expansion+" ", text)
            # text = re.sub(r'\b' + re.escape(abbr) + r'\b', expansion, text)  # LJ002-0055
            text = re.sub(abbr, expansion, text)

        # for abbr, expansion in self.abbreviations.items():
        #     # pattern = re.compile(re.escape(abbr), flags=re.IGNORECASE)
        #     pattern = re.compile(f"{abbr} ", flags=re.IGNORECASE)
        #     text = pattern.sub(expansion, text)
        return text

    # def convert_numbers_to_words(self, text):
    #     """Convert numeric digits into words."""
    #     text = re.sub(r'\d+',w2n.word_to_num(text), text)
    #     return text
    def number_to_words(self,text):
        def replace(match):
            num = int(match.group())
            return num2words(num)
        return re.sub(r'\b\d+\b', replace, text)

    def tokenize_with_punctuation(self, text):
        """Tokenizes text, treating commas as separate tokens."""
        # This regex keeps alphanumeric sequences and commas as separate tokens
        return re.findall(r'\w+|[,.!?;:"\'()]', text)

    def remove_punctuation(self, text):
        """Remove punctuation marks from the text.(!"#$%&'()*+,-./:;<=>?@[\]^_`{|})"""
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text

    def remove_extra_spaces(self, text):
        """Remove multiple spaces and trim leading/trailing spaces."""
        text = ' '.join(text.split())
        return text

    def expand_contractions(self, text):
        """Expand contractions like 'I'm' to 'I am'."""
        text = contractions.fix(text)
        return text

    def normalize_unicode(self, text):
        """Normalize unicode characters to a consistent form."""
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        return text

    def remove_urls_and_emails(self, text):
        """Remove URLs and email addresses from the text."""
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        return text
        
    def expand_urls_and_emails(self, text):        
        def expand_url(url):
            def expand_component(text):
                # Replace dots, slashes, and digits
                text = text.replace('.', ' dot ').replace('/', ' slash ')
                text = re.sub(r'\d+', lambda m: ' '.join(num2words(int(d)) for d in m.group()), text)
                return text

            if url.startswith("https://"):
                prefix = "h t t p s colon slash slash "
                url = url[len("https://"):]
            elif url.startswith("http://"):
                prefix = "h t t p colon slash slash "
                url = url[len("http://"):]
            else:
                prefix = ""

            normalized_url = prefix + expand_component(url)
            # print(normalized_url)
            normalized_url = re.sub(r'\s+', ' ', normalized_url).strip()
            return normalized_url
        
        text = re.sub(r'http\S+', lambda m: expand_url(m.group()), text)

        text = re.sub(r'([\w\.-]+)@([\w\.-]+)\.([a-z]{2,})',
                    lambda m: ''.join(m.group(1)) + ' at the rate ' + ''.join(m.group(2)) + ' dot ' + m.group(3),
                    text)

        return text

    def expand_alphanumeric(self, text):
        def replacer(match):
            token = match.group()
            # Split letters and digits
            return ' '.join([char.upper() if char.isalpha() else num2words(int(char)) for char in token])
        
        # Match tokens that have both letters and numbers
        return re.sub(r'\b(?=\w*[a-zA-Z])(?=\w*\d)\w+\b', replacer, text)

    # def expand_urls_and_emails(self, text):
    #     # for word, spoken in self.special_words.items():
    #     #     text = re.sub(r'\b' + word + r'\b', spoken, text, flags=re.IGNORECASE)
    #     # print(text)
    #     text = re.sub(r'https?://([\w.-]+)\.([a-z]{2,})(/[^\s]*)?',
    #                 lambda m: ' '.join(list('https')) + ' colon slash slash ' +
    #                             ''.join(m.group(1)) + ' dot ' + m.group(2) +
    #                             (' slash ' + m.group(3).replace('/', ' slash ') if m.group(3) else ''),
    #                 text)
        
    #     text = re.sub(r'([\w\.-]+)@([\w\.-]+)\.([a-z]{2,})',
    #                 lambda m: ''.join(m.group(1)) + ' at the rate ' + ''.join(m.group(2)) + ' dot ' + m.group(3),
    #                 text)
    #     return text

    def normalize_time(self,text):
        # Match time in 12-hour format (e.g., "10 am", "3:00 pm")
        text = re.sub(r'(\d{1,2}):(\d{2})\s*(am|pm)', r'\1:\2 \3', text, flags=re.IGNORECASE)
        text = re.sub(r'(\d{1,2})\s*(am|pm)', r'\1:00 \2', text, flags=re.IGNORECASE)  # Standardize to HH:MM AM/PM
        return text
    
    # hamndle panctution (for pause ,rythm )
    def clean_text_for_g2p(text):
        text = text.lower()
        text = re.sub(r"[,]", " PAUSE ", text)  # preserve pause info
        text = re.sub(r"[.?!]", " PAUSE ", text)  # optional: treat sentence end as pause
        text = re.sub(r"[^a-zA-Z0-9\sPAUSE]", "", text)  # remove other punctuation
        text = re.sub(r"\s+", " ", text).strip()  # clean extra spaces
        return text
    
    # def tag_pos(self,text):
    #     return pos_tag(text)

    # def tag_pos(self, text):
    #     tokens = word_tokenize(text)
    #     return pos_tag(tokens)

    def normalize_text(self, text):
        # text = text.lower()  # Lowercase the text
        text = self.expand_contractions(text)  # Expand contractions        
        text = self.expand_abbreviations(text)  # Expand abbreviations        
        text = self.remove_extra_spaces(text)  # Remove extra spaces        
        text = self.normalize_unicode(text)  # Normalize unicode
        # pos_tags = self.tag_pos(text)
        # text = self.normalize_time(text)  # Normalize time
        text = self.expand_urls_and_emails(text)  # Expand URLs and emails
        text = self.expand_alphanumeric(text) 
        text = self.number_to_words(text)  # Convert numbers to words        
        text = self.remove_punctuation(text)  # Remove punctuation        
        # return text
        return text
        
        # return {
        #     "normalized_text":text,
        # }
    

    # def normalize_text_for_g2p(self, text):
    #     text = text.lower()  # Lowercase the text
    #     text = self.expand_contractions(text)  # Expand contractions
    #     text = self.expand_abbreviations(text)  # Expand abbreviations
    #     text = self.remove_extra_spaces(text)  # Remove extra spaces
    #     text = self.normalize_unicode(text)  # Normalize unicode
    #     text = self.expand_urls_and_emails(text)  # Expand URLs and emails
    #     text = self.expand_alphanumeric(text)
    #     text = self.number_to_words(text)  # Convert numbers to words
    #     tokens = self.tokenize_with_punctuation(text) # Tokenize, keeping commas
    #     # cleaned_tokens = self.remove_other_punctuation(tokens) # Remove other unwanted punctuation
    #     return tokens # Return a list of tokens, including comma

    # def normalize_text_for_pos_tagging(self, text):
    #     text = text.lower()
    #     text = self.expand_contractions(text)
    #     text = self.expand_abbreviations(text)
    #     text = self.remove_extra_spaces(text)
    #     text = self.normalize_unicode(text)
    #     return self.tag_pos(text)
    
    # def text_to_phonemes(self, text):
    #     """Convert text to phonemes."""
    #     text = self.normalize_text(text)  # Normalize the text first
    #     phonemes = []
    #     # Use phonemizer for ARPAbet or CMU Dictionary for word-level phonemes
    #     words = text.split()
    #     for word in words:
    #         if word_phonemes:
    #             phonemes.append(word_phonemes)
    #         else:
    #             # If phonemizer doesn't return a result, check CMU Pronouncing Dictionary
    #             cmu_phonemes = pronouncing.phones_for_word(word)
    #             if cmu_phonemes:
    #                 phonemes.append(cmu_phonemes[0])  # Take the first pronunciation variant
    #             else:
    #                 phonemes.append(word)
    #     return phonemes


if __name__ == "__main__":

    from hybrid_G2P import G2PConverter
    # print(os.path.dirname(__file__))
    normalizer = TextNormalizer()
    raw_text = "Dr. Smith is going to the store. Visit http://www.example.com/test123//shruti.com/page or email me at test@example.com! I'm excited, No. 1 fan! c34545"

    normalized_text = normalizer.normalize_text(raw_text)
    print("Original Text:", raw_text)
    print("Normalized Text:", normalized_text)

    g2p=G2PConverter("avatar_ui/TTS_pipeline/models/3model_cnn.keras")
    # phonemes=g2p.predict(normalized_text['normalized_text'])
    phonemes=g2p.predict(normalized_text)
    print(phonemes)

    # texts = [
    #     "Printing, in the only sense with which we are at present concerned, differs from most if not from all the arts and crafts represented in the Exhibition",
    #     "Hello world! testone",
    #     "The quick brown fox jumps over the lazy dog.",
    #     "long narrow rooms -- one thirty-six feet, six twenty-three feet, and the eighth eighteen i.e. e.g.",
    #     "G2P batch test.",
    #     "in being comparatively modern.",
    #     "the recommendations we have here suggested would greatly advance the security of the office without any one two impairment of our fundamental liberties."
    # ]

    # normalized = [normalizer.normalize_text(t) for t in texts]
    # print(normalized)
    # phonemes = g2p.batch_predict(normalized)
    # # print('========',phonemes)
    # for t, p in zip(texts, phonemes):
    #     print(f"Text: {t}")
    #     print(f"Phonemes: {p}")
    #     print("---")

