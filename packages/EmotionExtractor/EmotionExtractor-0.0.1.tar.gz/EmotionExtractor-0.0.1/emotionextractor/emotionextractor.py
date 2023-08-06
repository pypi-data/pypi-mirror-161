# general imports
import re
import nltk
import logging
import pickle


class EmotionExtractor:
    def __init__(self):
        self.emo_extract_lex = None
        import os
        
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.DEBUG)

        try:
          file = os.path.join(os.path.dirname(__file__), "data/data.pkl")
          with open(file, "rb") as f:
              self.emo_extract_lex = pickle.load(f)
        except Exception as e:
          self.logger.error('failed to read emo_extract_lex file: %s', e)
          raise Exception(e)
          

    def tokenizer(self, sentence):
        """
        tokenizes sentence to word tokens using nltk
        """
        word_tokens = []
        from nltk.tokenize import word_tokenize

        nltk.download("punkt")

        if type(sentence) == str:
            word_tokens = word_tokenize(sentence)
            return word_tokens
        elif type(sentence) == list:
            return sentence
        else:
            self.logger.error("Cannot tokenize. Please input sentence")
            raise Exception("Cannot tokenize. Please input sentence")

    
    def remove_puncs_digits(self, tokens):
        """
        removes punctuations and digits using regex
        """
        cleaned_tokens = []
        for token in tokens:
            clean_token = re.sub("[^A-Za-z] ", "", token)
            if len(clean_token) > 0:
                cleaned_tokens.append(clean_token)

        self.logger.info("remove_puncs_digits: %s", cleaned_tokens)
        return cleaned_tokens

    
    def remove_stopwords(self, tokens):
        """
        removes stopwords using nltk
        """

        from nltk.corpus import stopwords

        nltk.download("stopwords")
        nltk.download("punkt")

        stop_words = set(stopwords.words("english"))
        filtered_sentence = [w for w in tokens if not w.lower() in stop_words]
        filtered_sentence = []

        for w in tokens:
            if w not in stop_words:
                filtered_sentence.append(w)

        self.logger.info("remove_stopwords: %s", filtered_sentence)
        return filtered_sentence

    
    def filter_by_pos(
        self, tokens, allowed_tags=["RB", "RBS", "RBR", "JJ", "JJR", "JJS"]
    ):
        """
        allowed tags can take in tags from this TAGSET list: https://github.com/nltk/nltk/blob/develop/nltk/app/chunkparser_app.py
        a more readable list from third party: https://www.guru99.com/pos-tagging-chunking-nltk.html
        """

        from nltk.corpus import wordnet as wn
        from nltk import pos_tag

        nltk.download("averaged_perceptron_tagger")

        sent = pos_tag(tokens)
        filtered = [s[0] for s in sent if s[1] in allowed_tags]

        self.logger.info("filter_by_pos: %s", filtered)
        return filtered

    
    def extract_emo_words(self, tokens):
        """
        extracts emotion words from tokens
        """
        emo_words = []
        for token in tokens:
            if token in self.emo_extract_lex:
                emo_words.append(token)

        self.logger.info("extract_emo_words: %s", emo_words)
        return emo_words

    
    def extract_emo_words_by_filter(self, tokens, filter):
        """
        extract negative emotion words from tokens
        """
        if filter != 'N' and filter != 'P':
          raise Exception('Only N and P are allowed as filter')
        
        emo_words = []
        for token in tokens:
            if token in self.emo_extract_lex and self.emo_extract_lex[token] == filter:
                emo_words.append(token)

        self.logger.info("extract_emo_words_by_filter: %s", emo_words)
        return emo_words


    def lemmatize_tokens(self, tokens):
        '''
        lemmatizes the tokens using WordNetLemmatizer
        '''
        from nltk.stem import WordNetLemmatizer

        nltk.download("wordnet")
        nltk.download("omw-1.4")

        lemmatizer = WordNetLemmatizer()
        lemmas = []
        lemma_dict = dict()
        for token in tokens:
            lemmatized = lemmatizer.lemmatize(token)
            lemmas.append(lemmatized)
            lemma_dict.update({lemmatized: token})
        # lemma dict is required to retrieve the original words in the input

        self.logger.info("lemmatize_tokens: %s", lemmas)
        return lemmas, lemma_dict

    
    def extract_emotion(
        self,
        s,
        lemmatize=False,
        clean_stopwords=True,
        remove_pos=False,
        allowed_pos=None,
        emotion_filter=None
    ):

        """
        runs all the emo extractor internal functions according the params supplied
        
        :param str|list s: input sentence or list of word tokens
        :param bool lemmatize: Set to True to enable lemmatization. default is False
        :param bool clean_stopwords: Set to False to disable stop words removal. default is True
        :param bool remove_pos: Set to True if you'd like to only allow certain Parts of speech (POS). default s false
        :param list allowed_pos: List of POS you want to allow from nltk TAGSET: https://github.com/nltk/nltk/blob/develop/nltk/app/chunkparser_app.py
        a more readable list from third party: https://www.guru99.com/pos-tagging-chunking-nltk.html When it is not set, and remove_pos is set to True, then by default this POS whitelist is used: ["RB", "RBS", "RBR", "JJ", "JJR", "JJS"]
        :param str filter: It can be set to either 'N' or 'P'. default is None.
        :return: emotion words
        :rtype: list
        
        """

        # mandatory steps
        t = self.tokenizer(s)
        t = self.remove_puncs_digits(t)

        # optional steps
        if clean_stopwords:
            t = self.remove_stopwords(t)

        if remove_pos:
            if allowed_pos is None:
                t = self.filter_by_pos(t)
            else:
                t = self.filter_by_pos(t, allowed_pos)

        if lemmatize:
            t, lemma_dct = self.lemmatize_tokens(t)

        if emotion_filter is not None:
            t = self.extract_emo_words_by_filter(t, emotion_filter)
        else:
            t = self.extract_emo_words(t)

        if lemmatize:
            unlemmatized = []
            for lemmas in t:
                unlemmatized.append(lemma_dct[lemmas])
            return unlemmatized

        return t
