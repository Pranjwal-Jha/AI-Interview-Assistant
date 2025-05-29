import re
import string
def preprocess_words(spoken_text:str):
    cleaned_text=re.sub(r'[^a-zA-Z0-9\s\.\'\?!]','',spoken_text).lower()
    return cleaned_text

