from bs4 import BeautifulSoup
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import os

# -------- Fix NLTK path --------
nltk_data_path = os.path.join(os.path.dirname(__file__),"nltk_data")

if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)

nltk.data.path.append(nltk_data_path)

# download only if missing
try:
    stopwords.words('english')
except:
    nltk.download('stopwords',download_dir=nltk_data_path)

try:
    nltk.data.find('corpora/wordnet')
except:
    nltk.download('wordnet',download_dir=nltk_data_path)
    nltk.download('omw-1.4',download_dir=nltk_data_path)

# -------- NLP processing --------
stop = stopwords.words('english')

lemmatizer = WordNetLemmatizer()

def review_to_words(raw_review):

    review_text = BeautifulSoup(raw_review,'html.parser').get_text()

    letters_only = re.sub('[^a-zA-Z]',' ',review_text)

    words = letters_only.lower().split()

    meaningful_words = [w for w in words if w not in stop]

    lemmatized = [lemmatizer.lemmatize(w) for w in meaningful_words]

    return ' '.join(lemmatized)