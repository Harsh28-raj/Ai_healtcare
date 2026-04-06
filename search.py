import pandas as pd
from rapidfuzz import process, fuzz
import joblib
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
print("Loading datasets in search.py...")
df_11k = pd.read_csv(os.path.join(DATA_DIR, 'medicines_11k.csv'))
df_az = pd.read_csv(os.path.join(DATA_DIR, 'medicines_az.csv'), low_memory=False)

df_11k['Medicine Name'] = df_11k['Medicine Name'].fillna('')
df_az['name'] = df_az['name'].fillna('')

names_11k = df_11k['Medicine Name'].tolist()
names_az = df_az['name'].tolist()

model_path = os.path.join(os.path.dirname(__file__), 'medicine_model.pkl')
category_model = joblib.load(model_path) if os.path.exists(model_path) else None
print("Datasets and model loaded successfully!")

# ─── Helpers ───

def get_alternatives(composition, exclude_name):
    if not composition or pd.isna(composition):
        return []
    comp_str = str(composition).strip()[:15]
    
    matches_11k = df_11k[
        (df_11k['Composition'].astype(str).str.contains(comp_str, case=False, na=False, regex=False)) &
        (df_11k['Medicine Name'].str.lower() != str(exclude_name).lower())
    ]
    if not matches_11k.empty:
        return matches_11k['Medicine Name'].head(3).tolist()
    
    matches_az = df_az[
        (df_az['short_composition1'].astype(str).str.contains(comp_str, case=False, na=False, regex=False)) &
        (df_az['name'].str.lower() != str(exclude_name).lower())
    ]
    return matches_az['name'].head(3).tolist()

# ─── Formatters ───

def format_11k_result(row):
    comp = str(row.get('Composition', ''))
    cat = category_model.predict([comp])[0] if category_model else "General Medicine"
    
    return {
        "name": str(row.get('Medicine Name', '')),
        "type": "Allopathy",
        "category": cat,
        "composition": comp,
        "uses": str(row.get('Uses', '')),
        "side_effects": str(row.get('Side_effects', '')),
        "manufacturer": str(row.get('Manufacturer', '')),
        "status": "Discontinued" if bool(row.get('Is_discontinued', False)) else "Active in Market",
        "alternatives": get_alternatives(comp, row.get('Medicine Name'))
    }

def format_az_result(row):
    c1 = str(row.get('short_composition1', '')).strip()
    c2 = str(row.get('short_composition2', '')).strip()
    comp = (c1 + " " + c2).strip() if c2 and c2 != 'nan' else c1
    cat = category_model.predict([comp])[0] if category_model else "General Medicine"
    
    uses = "N/A"
    side_effects = "N/A"
    comp_prefix = comp[:15]
    if comp_prefix:
        lookup = df_11k[df_11k['Composition'].astype(str).str.contains(comp_prefix, case=False, na=False, regex=False)]
        if not lookup.empty:
            lookup_row = lookup.iloc[0]
            uses = str(lookup_row.get('Uses', 'N/A'))
            side_effects = str(lookup_row.get('Side_effects', 'N/A'))
            
    if uses == "N/A" and cat != "General Medicine":
        uses = f"Used for {cat} conditions"
    elif uses == "N/A":
        uses = "Used for general medical conditions"
    
    return {
        "name": str(row.get('name', '')),
        "type": str(row.get('type', "Allopathy")),
        "category": cat,
        "composition": comp,
        "uses": uses,
        "side_effects": side_effects,
        "manufacturer": str(row.get('manufacturer_name', '')),
        "status": "Discontinued" if bool(row.get('Is_discontinued', False)) else "Active in Market",
        "alternatives": get_alternatives(comp, row.get('name'))
    }

# ─── Core Search ───

def search_medicine(query: str):
    q = query.strip()
    if not q:
        return None
    
    q_lower = q.lower()
    prefix_matches_11k = df_11k[df_11k['Medicine Name'].str.lower().str.startswith(q_lower)]
    if not prefix_matches_11k.empty:
        best_idx = prefix_matches_11k['Medicine Name'].str.len().idxmin()
        return format_11k_result(df_11k.iloc[best_idx])
    
    prefix_matches_az = df_az[df_az['name'].str.lower().str.startswith(q_lower)]
    if not prefix_matches_az.empty:
        best_idx = prefix_matches_az['name'].str.len().idxmin()
        return format_az_result(df_az.iloc[best_idx])
    
    match_11k = process.extractOne(q, names_11k, scorer=fuzz.WRatio)
    match_az = process.extractOne(q, names_az, scorer=fuzz.WRatio)

    best_score = 0
    best_match = None
    source = None

    if match_11k and match_11k[1] >= 75:
        best_score = match_11k[1]
        best_match = match_11k
        source = '11k'

    if match_az and match_az[1] >= 75 and match_az[1] > best_score:
        best_score = match_az[1]
        best_match = match_az
        source = 'az'

    if not best_match:
        return None

    if source == '11k':
        return format_11k_result(df_11k.iloc[best_match[2]])
    else:
        return format_az_result(df_az.iloc[best_match[2]])

# ─── Suggest / Autocomplete ───

def suggest_medicine(query: str):
    q = query.strip().lower()
    if not q:
        return []
    
    suggestions = []
    
    prefix_11k = df_11k[df_11k['Medicine Name'].str.lower().str.startswith(q)]
    if not prefix_11k.empty:
        sorted_prefix = prefix_11k.sort_values(by='Medicine Name', key=lambda x: x.str.len())
        suggestions.extend(sorted_prefix['Medicine Name'].head(5).tolist())
    
    if len(suggestions) < 5:
        prefix_az = df_az[df_az['name'].str.lower().str.startswith(q)]
        if not prefix_az.empty:
            sorted_prefix = prefix_az.sort_values(by='name', key=lambda x: x.str.len())
            suggestions.extend(sorted_prefix['name'].head(5 - len(suggestions)).tolist())
    
    if len(suggestions) < 5:
        fuzzy_11k = process.extract(query, names_11k, scorer=fuzz.WRatio, limit=5)
        for m in fuzzy_11k:
            if m[1] >= 75 and m[0] not in suggestions:
                suggestions.append(m[0])
                if len(suggestions) >= 5:
                    break
    
    return suggestions[:5]