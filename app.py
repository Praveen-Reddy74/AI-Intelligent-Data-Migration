# ------------------------------------
# STREAMLIT SANKEY – AI COLUMN MAPPING
# (FINAL POLISHED VERSION)
# ------------------------------------

import streamlit as st
import pandas as pd
import difflib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from db_utils import get_pg_data
import plotly.graph_objects as go


# ------------------------------------
# STREAMLIT PAGE CONFIG
# ------------------------------------
st.set_page_config(
    page_title="AI Column Mapping – Sankey",
    layout="wide"
)

st.title("🔗 AI-Based Column Mapping (Source → Target)")
st.markdown(
    "This Sankey diagram visualizes how **source columns** are mapped to "
    "**target columns**, where link thickness represents mapping confidence."
)


# ------------------------------------
# LOAD SOURCE (SAMPLED)
# ------------------------------------
source_df = get_pg_data(
    db="insurance_source",
    query="SELECT * FROM insurance_raw",
    limit=2000
)

# ------------------------------------
# LOAD TARGET (SCHEMA ONLY)
# ------------------------------------
target_df = get_pg_data(
    db="insurance_target",
    query="SELECT * FROM policy_holders",
    limit=0
)

source_cols = source_df.columns.tolist()
target_cols = target_df.columns.tolist()


# ------------------------------------
# AI SIMILARITY FUNCTIONS
# ------------------------------------
def text_similarity(a, b):
    tfidf = TfidfVectorizer().fit_transform([a, b])
    return cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]


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


# ------------------------------------
# BUILD AI MAPPING
# ------------------------------------
mappings = []

for src in source_cols:
    best_match = None
    best_score = 0

    for tgt in target_cols:
        tfidf_score = text_similarity(src.replace("_", " "), tgt.replace("_", " "))
        seq_score = difflib.SequenceMatcher(None, src, tgt).ratio()
        final_score = (tfidf_score + seq_score) / 2 + heuristic_boost(src, tgt)

        if final_score > best_score:
            best_score = final_score
            best_match = tgt

    mappings.append({
        "source": src,
        "target": best_match,
        "confidence": round(best_score, 2)
    })

mapping_df = pd.DataFrame(mappings)


# ------------------------------------
# CONFIDENCE FILTER
# ------------------------------------
threshold = st.slider(
    "Minimum confidence to display",
    min_value=0.0,
    max_value=1.0,
    value=0.6,
    step=0.05
)

filtered_df = mapping_df[mapping_df["confidence"] >= threshold]
filtered_df = filtered_df.sort_values(by="confidence", ascending=False)


# ------------------------------------
# BUILD SANKEY STRUCTURE (NO OVERLAP)
# ------------------------------------
source_labels = filtered_df["source"].unique().tolist()
target_labels = filtered_df["target"].unique().tolist()

labels = source_labels + target_labels
label_index = {label: i for i, label in enumerate(labels)}

sources = filtered_df["source"].map(label_index).tolist()
targets = filtered_df["target"].map(label_index).tolist()

# Scale confidence to improve link thickness
values = [v * 10 for v in filtered_df["confidence"].tolist()]


# ------------------------------------
# SANKEY DIAGRAM
# ------------------------------------
fig = go.Figure(
    data=[
        go.Sankey(
            arrangement="snap",
            node=dict(
                pad=35,                     # vertical spacing
                thickness=25,               # node size
                line=dict(color="black", width=0.5),
                label=labels,
                color=(
                    ["#4C78A8"] * len(source_labels) +
                    ["#F58518"] * len(target_labels)
                )
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color="rgba(180,180,180,0.6)"
            )
        )
    ]
)

fig.update_layout(
    height=750,
    margin=dict(l=40, r=40, t=40, b=40)
)

st.plotly_chart(fig, use_container_width=True)


# ------------------------------------
# MAPPING TABLE (REFERENCE)
# ------------------------------------
st.markdown("### 📋 Column Mapping Details")
st.dataframe(mapping_df)
