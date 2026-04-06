import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
import os

def get_category_label(composition):
    comp = str(composition).lower()
    if any(x in comp for x in ['paracetamol', 'ibuprofen']):
        return 'Pain Relief / Antipyretic'
    elif any(x in comp for x in ['amoxicillin', 'azithromycin', 'ciprofloxacin']):
        return 'Antibiotic'
    elif any(x in comp for x in ['omeprazole', 'pantoprazole', 'ranitidine']):
        return 'Antacid'
    elif any(x in comp for x in ['furosemide', 'spironolactone', 'amlodipine']):
        return 'Cardiac / Diuretic'
    elif any(x in comp for x in ['metformin', 'glimepiride', 'insulin']):
        return 'Antidiabetic'
    elif any(x in comp for x in ['vitamin', 'zinc', 'iron', 'calcium']):
        return 'Supplement'
    elif any(x in comp for x in ['cetirizine', 'loratadine', 'montelukast']):
        return 'Antiallergic'
    return 'General Medicine'

def train_and_save_model():
    print("Loading datasets...")
    # Adjust paths based on deployment or script execution location
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'medicines_11k.csv')
    df = pd.read_csv(data_path)
    
    print("Generating labels from Composition...")
    df['Composition'] = df['Composition'].fillna('')
    df['Category'] = df['Composition'].apply(get_category_label)
    
    print("Training model...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english')),
        ('clf', LogisticRegression(max_iter=1000, class_weight='balanced'))
    ])
    
    pipeline.fit(df['Composition'], df['Category'])
    
    model_path = os.path.join(os.path.dirname(__file__), 'medicine_model.pkl')
    print(f"Saving model to {model_path}...")
    joblib.dump(pipeline, model_path)
    print("Done!")

if __name__ == "__main__":
    train_and_save_model()
