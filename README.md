# AI-Powered Intelligent Data Migration System

## Overview
This project demonstrates an AI-assisted data migration system that understands schema semantics, suggests intelligent mappings, explains decisions, validates data, and visualizes source-to-target relationships.

## Problem Addressed
Traditional data migration relies on manual rules and scripts, making it error-prone, hard to audit, and difficult to scale. This system introduces intelligence and explainability into the migration process.

## Key Features
- Automatic schema discovery
- AI-based column mapping with confidence scores
- Explainable mapping logic
- Safe data migration with transformations
- Validation reports
- Sankey-based visualization for auditability

## Tech Stack
- Python
- PostgreSQL
- Pandas
- Streamlit
- Plotly
- Scikit-learn

flowchart TD
    A[Source Database<br>PostgreSQL] --> B[Schema Discovery]
    B --> C[Sample Data Extraction]
    C --> D[AI Column Mapping Engine]

    D --> E{Confidence > Threshold?}
    E -->|Yes| F[Accept Mapping]
    E -->|No| G[Flag for Review]

    F --> H[Explainability Layer]
    G --> H

    H --> I[Migration & Transformation]
    I --> J[Target Database<br>PostgreSQL]

    J --> K[Validation Framework]
    K --> L[Sankey Visualization<br>Dashboard]


## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py

