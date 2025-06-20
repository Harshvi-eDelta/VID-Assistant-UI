import pandas as pd
import numpy as np
import tensorflow as tf
import ast
from nltk.corpus import cmudict


class G2PConverter:
    # def __init__(self, model_path=None, vocab_path="dataset/G2P_dataset/cmu_dict_no_stress.csv", max_len=33, load_model=True):
    # def __init__(self, model_path=None, vocab_path="dataset/G2P_dataset/cmu_dict_pun_stress.csv", max_len=33, load_model=True):
    def __init__(self, model_path=None, vocab_path="avatar_ui/TTS_pipeline/dataset/cmu_dict_with_stress.csv", max_len=33, load_model=True):
        self.max_len = max_len
        self.phoneme_dict=cmudict.dict()
        # print(self.phoneme_dict.keys())
        if load_model and model_path:
            self.model = tf.keras.models.load_model(model_path)
        self._load_vocab(vocab_path)
        
        # pd.DataFrame({'keys': [i for i in self.phoneme_dict.keys() if len(i)==1]}).to_csv("key_val.csv", index=False)

    def _load_vocab(self, vocab_path):
        df = pd.read_csv(vocab_path)        
        self.words = df["word"].tolist()
        # self.phonemes = self._phoneme_string_to_list(df["phonemes"].tolist())
        self.phonemes = df["phonemes"].apply(ast.literal_eval).tolist()

        # Build grapheme vocab
        graphemes = sorted(set(ch for w in self.words for ch in str(w)))
        self.char2idx = {c: i + 1 for i, c in enumerate(graphemes)}
        self.char2idx['<pad>'] = 0
        self.char2idx['<sos>'] = len(self.char2idx)
        self.char2idx['<eos>'] = len(self.char2idx)
        self.idx2char = {i: c for c, i in self.char2idx.items()}
        print(self.char2idx)

        # Build phoneme vocab
        phoneme_set = sorted(set(p for ph in self.phonemes for p in ph))
        self.phn2idx = {p: i + 1 for i, p in enumerate(phoneme_set)}
        self.phn2idx['<pad>'] = 0
        self.phn2idx['<sos>'] = len(self.phn2idx)
        self.phn2idx['<eow>'] = len(self.phn2idx)
        self.phn2idx['<eos>'] = len(self.phn2idx)
        self.idx2phn = {i: p for p, i in self.phn2idx.items()}
        print(self.phn2idx)

    def _phoneme_string_to_list(self, phoneme_strs):
        return [p.split() for p in phoneme_strs]

    def _encode_sequences(self, data, token2idx, maxlen=None):
        encoded = []
        for seq in data:
            s = [token2idx.get(c, token2idx['<pad>']) for c in seq]
            encoded.append(s)
        max_len = maxlen or max(len(s) for s in encoded)
        # print(max_len)
        padded = [s + [token2idx['<pad>']] * (max_len - len(s)) for s in encoded]
        # print(padded)
        return np.array(padded)

    def preprocess_input(self, text):
        text = text.lower()
        words = text.strip().split()
        # encoded_words = [self._encode_sequences([w], self.char2idx, maxlen=self.max_len) for w in words]
        return words

    def word_to_phonemes(self, word):
        # print("***",word)
        phoneme = self.phoneme_dict.get(word, None)
        # print(phoneme)
        if phoneme is not None:
            phoneme_token=self._encode_sequences([phoneme[0]], self.phn2idx) 
            return phoneme[0],phoneme_token[0].tolist()

        encoded_words = self._encode_sequences([word], self.char2idx, maxlen=self.max_len) 
        # print("encoded_word: ",encoded_words)
        preds = self.model.predict(encoded_words, verbose=0)
        phoneme_token = np.argmax(preds, axis=-1)[0]
        # # print(phoneme_token,self.phn2idx['<pad>'])
        # phoneme_token = [int(id) for id in phoneme_token if id != self.phn2idx['<pad>']]
        phoneme_token = [int(id) for id in phoneme_token if id != self.phn2idx['<pad>'] and id != self.phn2idx['<eow>']]
        phoneme = [self.idx2phn.get(i, "<unk>") for i in phoneme_token if i != self.phn2idx['<pad>']] 
        return phoneme,phoneme_token

    def predict(self, text):
        words = self.preprocess_input(text)
        # predicted_phonemes = [[self.phn2idx['<sos>']]]
        predicted_phonemes = []
        pre_phoneme=[]

        for w in words:
            phonemes,phoneme_token = self.word_to_phonemes(w)
            # p = copy.deepcopy(phonemes)
            p = phoneme_token.copy()
            # p = phonemes            
            p.append(self.phn2idx['<eow>'])
            predicted_phonemes.append(p)

        predicted_phonemes.append([self.phn2idx['<eos>']])
        flat_phonemes = [p for word in predicted_phonemes for p in word] 
        return flat_phonemes
    
    def batch_predict(self, texts):
        # Step 1: Normalize input
        # preprocessed_sentences = [self.g2p.preprocess_input(text) for text in texts]
        preprocessed_sentences = [self.preprocess_input(t) for t in texts]
        # print(preprocessed_sentences)
        # Step 2: Identify known (in dict) vs OOV (need prediction) words
        flat_words = [word for sent in preprocessed_sentences for word in sent]
        # print(flat_words)
        known = []
        oov = []
        for word in flat_words:
            if word not in self.phoneme_dict:
                oov.append(word)
            # else:
        # print(known)
        # Step 3: Predict phonemes for OOV words
        oov_unique = list(set(oov))
        oov_encoded = self._encode_sequences(oov_unique, self.char2idx, maxlen=self.max_len)    
        preds = self.model.predict(oov_encoded, verbose=0)

        oov_results = {}
        for word, pred in zip(oov_unique, preds):
            phoneme_token = np.argmax(pred, axis=-1)
            phoneme_token = [int(id) for id in phoneme_token if id != self.phn2idx['<pad>'] and id != self.phn2idx['<eow>']]
            # phoneme_token = [int(id) for id in phoneme_token if id != self.phn2idx['<pad>']]
            # phns = [self.idx2phn.get(i, "<unk>") for i in phoneme_token]
            # phns.append(self.phn2idx['<eow>'])
            phoneme_token.append(self.phn2idx['<eow>'])
            # phns.append('<eow>')
            oov_results[word] = phoneme_token

        # print(oov_results)
        # Step 4: Reconstruct sentences
        result = []
        i = 0
        for sent in preprocessed_sentences:
            sentence_phonemes = []
            for word in sent:
                if word in self.phoneme_dict:
                    # p=self.phoneme_dict[word][0]
                    # phns=p.copy()
                    # print(phns)
                    encoded_phoneme=self._encode_sequences([self.phoneme_dict[word][0]], self.phn2idx)[0].tolist()
                    # print(encoded_phoneme,self.phoneme_dict[word][0])
                    encoded_phoneme.append(self.phn2idx['<eow>'])
                    # phns.append('<eow>')
                    # print(encoded_phoneme)
                    sentence_phonemes += encoded_phoneme 
                else:
                    sentence_phonemes += oov_results[word]
                i += 1
            sentence_phonemes.append(self.phn2idx['<eos>'])
            result.append(sentence_phonemes)

        return result

    # def batch_predict(self, texts):
    #     # Step 1: Preprocess each sentence into list of words
    #     print(texts)
    #     batch_encoded = [self.preprocess_input(t) for t in texts]  # List[List[np.array]]
    #     print(batch_encoded)
    #     # Step 2: Flatten all words from all sentences for batch prediction
    #     flat_inputs = [item for sentence in batch_encoded for item in sentence]
    #     print(flat_inputs)
    #     # Step 3: Run prediction on the flat input
    #     preds = self.model.predict(np.vstack(flat_inputs), verbose=1)
    #     print(preds)
    #     # Step 4: Convert predictions back to phonemes
    #     flat_results = []

    #     for pred in preds:
    #         phoneme_token = np.argmax(pred, axis=-1)
    #         phoneme_token = [int(id) for id in phoneme_token if id != self.phn2idx['<pad>'] and id != self.phn2idx['<eow>']]
    #         # phoneme_token = [int(id) for id in phoneme_token if id != self.phn2idx['<pad>']]
    #         phoneme_token.append(self.phn2idx['<eow>'])
    #         phns = [self.idx2phn.get(i, "<unk>") for i in phoneme_token if i != self.phn2idx['<pad>']]
    #         # print("===",phns)
    #         # flat_results.append(phoneme_token)
    #         flat_results.append(phns)
    #     # Step 5: Reconstruct sentence-level phoneme list
    #     # print(flat_results)
    #     results = []
    #     i = 0
    #     for sentence in batch_encoded:
    #         # print(sentence)
    #         num_words = len(sentence)
    #         sentence_phonemes = flat_results[i:i+num_words]  # List of lists
    #         # print("******",sentence_phonemes)  
    #         # sentence_flat =[self.phn2idx['<sos>']] + [ph for word in sentence_phonemes for ph in word] + [self.phn2idx['<eos>']] #  sos(40) + Flatten word-level phonemes + eos(41)
    #         sentence_flat =[ph for word in sentence_phonemes for ph in word] + [self.phn2idx['<eos>']] #  sos(40) + Flatten word-level phonemes + eos(41)
    #         # sentence_flat =[ph for word in sentence_phonemes for ph in word] 
    #         results.append(sentence_flat)
    #         # print(results)
    #         i += num_words
    #     return results