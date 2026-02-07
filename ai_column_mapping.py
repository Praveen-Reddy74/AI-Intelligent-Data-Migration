# -----------------------------
# AI COLUMN MAPPING (FULL FILE)
# -----------------------------

from db_utils import get_pg_data
import pandas as pd
import difflib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# -----------------------------
# STEP 1: LOAD SOURCE (SAMPLED)
# -----------------------------
source_df = get_pg_data(
    db="insurance_source",
    query="SELECT * FROM insurance_raw",
    limit=2000   # IMPORTANT: sampling
)


# -----------------------------
# STEP 2: LOAD TARGET (SCHEMA ONLY)
# -----------------------------
target_df = get_pg_data(
    db="insurance_target",
    query="SELECT * FROM policy_holders",
    limit=0      # IMPORTANT: schema only
)


# -----------------------------
# STEP 3: EXTRACT COLUMN NAMES
# -----------------------------
source_cols = source_df.columns.tolist()
target_cols = target_df.columns.tolist()

print("\nSource Columns:")
print(source_cols)

print("\nTarget Columns:")
print(target_cols)


# -----------------------------
# STEP 4: BASE AI SIMILARITY
# -----------------------------
def text_similarity(a, b):
    tfidf = TfidfVectorizer().fit_transform([a, b])
    return cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]


# -----------------------------
# STEP 5: DOMAIN HEURISTICS
# (this fixes flat scores)
# -----------------------------
DOMAIN_HINTS = {
    "id": ["id", "holder"],
    "gender": ["sex"],
    "age": ["age"],
    "annual": ["premium"],
    "vehicle": ["vehicle", "category"],
    "region": ["location", "state", "city"],
    "response": ["claim", "flag"]
}

def heuristic_boost(src, tgt):
    boost = 0
    src_l = src.lower()
    tgt_l = tgt.lower()

    for key, hints in DOMAIN_HINTS.items():
        if key in src_l:
            for h in hints:
                if h in tgt_l:
                    boost += 0.3
    return boost


# -----------------------------
# STEP 6: AI MAPPING LOGIC
# -----------------------------
mappings = []

for src_col in source_cols:
    best_match = None
    best_score = 0

    for tgt_col in target_cols:
        tfidf_score = text_similarity(
            src_col.replace("_", " "),
            tgt_col.replace("_", " ")
        )

        seq_score = difflib.SequenceMatcher(
            None, src_col, tgt_col
        ).ratio()

        final_score = (
            (tfidf_score + seq_score) / 2
            + heuristic_boost(src_col, tgt_col)
        )

        if final_score > best_score:
            best_score = final_score
            best_match = tgt_col

    mappings.append({
        "source_column": src_col,
        "target_column": best_match,
        "confidence": round(best_score, 2)
    })


# -----------------------------
# STEP 7: SHOW RESULTS
# -----------------------------
mapping_df = pd.DataFrame(mappings)

print("\nAI Column Mapping Results:\n")
print(mapping_df)
