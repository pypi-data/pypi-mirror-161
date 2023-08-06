# EmotionExtractor
Extract emotion words from sentence or list of tokens.

# Usage
```python
ee = EmotionExtractor()

sentence = "I am happy to see you succeed"
tokens = ["I", "am", "happy", "to", "see", "you", "succeed"]

ee.extract_emotion(sentence)
#or 
ee.extract_emotion(tokens)
```

`extract_emotion(...)` can take several other optional parameters in addition to input sentence/word tokens:

```
:param bool lemmatize: Set to True to enable lemmatization. default is False
:param bool clean_stopwords: Set to False to disable stop words removal. default is True
:param bool remove_pos: Set to True if you'd like to only allow certain Parts of speech (POS). default s false
:param list allowed_pos: List of POS you want to allow from nltk TAGSET: https://github.com/nltk/nltk/blob/develop/nltk/app/chunkparser_app.py
a more readable list from third party: https://www.guru99.com/pos-tagging-chunking-nltk.html When it is not set, and remove_pos is set to True, then by default this POS whitelist is used: ["RB", "RBS", "RBR", "JJ", "JJR", "JJS"]
:param str filter: It can be set to either 'N' or 'P'. default is None.
```


# Troubleshooting:
If you recieve error regarding `nltk version not found` try:

```bash
pip install --upgrade nltk
```



