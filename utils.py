import re
from bs4 import BeautifulSoup

def review_to_words(text):

    text = BeautifulSoup(text,"html.parser").get_text()

    text = re.sub("[^a-zA-Z]"," ",text)

    return text.lower()