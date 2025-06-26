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
                ('ave','avenue'),
            ]]

    def expand_abbreviations(self, text):
        """Expands known abbreviations in the text."""
        for abbr, expansion in self.abbreviations:            
            text = re.sub(abbr, expansion, text)

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
            return ' '.join([char.upper() if char.isalpha() else num2words(int(char)) for char in token])
        return re.sub(r'\b(?=\w*[a-zA-Z])(?=\w*\d)\w+\b', replacer, text)

    def normalize_time(self,text):
        # Match time in 12-hour format (e.g., "10 am", "3:00 pm")
        text = re.sub(r'(\d{1,2}):(\d{2})\s*(am|pm)', r'\1:\2 \3', text, flags=re.IGNORECASE)
        text = re.sub(r'(\d{1,2})\s*(am|pm)', r'\1:00 \2', text, flags=re.IGNORECASE)
        return text
    
    def clean_text_for_g2p(text):
        text = text.lower()
        text = re.sub(r"[,]", " PAUSE ", text) 
        text = re.sub(r"[.?!]", " PAUSE ", text)
        text = re.sub(r"[^a-zA-Z0-9\sPAUSE]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text
    
    # def tag_pos(self,text):
    #     return pos_tag(text)

    # def tag_pos(self, text):
    #     tokens = word_tokenize(text)
    #     return pos_tag(tokens)

    def normalize_text(self, text):
        # text = text.lower()
        text = self.expand_contractions(text)
        text = self.expand_abbreviations(text)
        text = self.remove_extra_spaces(text)
        text = self.normalize_unicode(text)
        # pos_tags = self.tag_pos(text)
        # text = self.normalize_time(text)
        text = self.expand_urls_and_emails(text) 
        text = self.expand_alphanumeric(text) 
        text = self.number_to_words(text)  
        text = self.remove_punctuation(text)
        return text


