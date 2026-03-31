import re
from bs4 import BeautifulSoup

def review_to_words(raw_review):

    # remove html
    review_text = BeautifulSoup(raw_review,"html.parser").get_text()

    # keep letters only
    letters_only = re.sub("[^a-zA-Z]"," ",review_text)

    # lowercase
    words = letters_only.lower().split()

    return " ".join(words)