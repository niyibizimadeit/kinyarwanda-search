# Kinyarwanda-English Bilingual Search Engine

A hybrid NLP search system that handles code-switched Kinyarwanda-English queries — a genuinely novel problem with no off-the-shelf solution. Built for real-world deployment on a Rwandan e-commerce platform, with a research paper and public dataset as parallel outputs.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![arXiv](https://img.shields.io/badge/arXiv-coming_soon-red.svg)]()
[![Dataset](https://img.shields.io/badge/Dataset-Zenodo-blue.svg)]()
[![Demo](https://img.shields.io/badge/Demo-Streamlit-ff4b4b.svg)](https://YOUR_APP.streamlit.app)

---

## The problem

Rwanda's digital economy is bilingual in practice but monolingual in infrastructure. Real users search in Kinyarwanda, in English, and in mixed queries like:

```
"ndashaka ibicuruzwa bya phone nziza"   → I want good phone products
"laptop price muri Kigali"              → laptop price in Kigali
"agaseke ka laptop"                     → laptop bag
```

No existing search engine is built for this. Standard English NLP pipelines drop Kinyarwanda tokens. Off-the-shelf multilingual models are not trained on Rwandan e-commerce vocabulary. This project closes that gap.

---

## What this system does

- Accepts queries in **Kinyarwanda, English, or any mix of both**
- Returns ranked product results using a **hybrid TF-IDF + multilingual embedding pipeline**
- Runs as a **Supabase RPC function** — one call from any frontend
- Ships with a **Streamlit demo UI** showing e-commerce search, logistics landmark search, and a 2-in-1 mode
- Includes a **citable Kinyarwanda e-commerce vocabulary lexicon** published on Zenodo

---

## Architecture

```
Mixed query input  (e.g. "ndashaka phone nziza")
        │
        ▼
Query preprocessor
  - Tokenize and normalize
  - Detect language composition (EN / RW / mixed)
        │
   ┌────┴─────┐
   ▼          ▼
TF-IDF    Semantic embeddings
retriever  (multilingual MiniLM)
   │          │
   └────┬─────┘
        ▼
Hybrid reranker
  score = α · TF-IDF + β · cosine similarity
        │
        ▼
Ranked product results
```

---

## Project structure

```
kinyarwanda-search/
├── data/
│   ├── raw/                  # Synthetic bilingual product catalog + query dataset
│   └── processed/            # TF-IDF matrix, processed embeddings
├── models/                   # Downloaded model weights (gitignored)
├── search/
│   ├── __init__.py
│   ├── preprocessor.py       # Tokenization, normalization, language detection
│   ├── tfidf_retriever.py    # Bilingual TF-IDF index
│   ├── embedding_retriever.py # Multilingual sentence embeddings
│   └── hybrid_search.py      # Score fusion and reranking
├── api/
│   ├── __init__.py
│   └── main.py               # FastAPI search endpoint
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_tfidf_baseline.ipynb
│   └── 03_evaluation.ipynb
├── demo/
│   └── app.py                # Streamlit demo (e-commerce / logistics / 2-in-1)
├── paper/
│   └── kinyarwanda_search.tex # Research paper (LaTeX)
├── sql/
│   └── migration.sql         # Supabase schema migration
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Tech stack

| Component | Tool |
|---|---|
| TF-IDF index | scikit-learn `TfidfVectorizer` |
| Sentence embeddings | `paraphrase-multilingual-MiniLM-L12-v2` |
| Vector storage | Supabase pgvector (`vector(512)`) |
| API layer | FastAPI |
| Demo UI | Streamlit |
| Frontend integration | Next.js + Supabase RPC |

---

## Dataset

The project includes the first publicly documented Kinyarwanda e-commerce dataset:

- **Product catalog** — 300 products with English and Kinyarwanda names, descriptions, categories
- **Query dataset** — 300 mixed-language search queries with relevance annotations
- **Vocabulary lexicon** — ~80 Kinyarwanda commerce terms with English translations
- **Kigali landmarks** — Real sector and landmark names for logistics demo

All datasets are registered on Zenodo with a permanent DOI and are freely available for research use.

---

## Evaluation

| Mode | MRR | NDCG@5 |
|---|---|---|
| TF-IDF only | — | — |
| Embeddings only | — | — |
| Hybrid (α=0.4, β=0.6) | — | — |

*Results will be populated after experiments in Phase 3.*

---

## Getting started

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/kinyarwanda-search.git
cd kinyarwanda-search

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the demo
streamlit run demo/app.py
```

---

## Research paper

A companion paper documenting the dataset construction methodology, system design, and evaluation results is in preparation for arXiv submission.

> NIYIBIZI Prince. *Hybrid Bilingual Search for Kinyarwanda-English Code-Switched E-Commerce Queries.* arXiv, 2025.

---

## License

MIT License © 2025 NIYIBIZI Prince

---

## Acknowledgements

Built on top of [sentence-transformers](https://www.sbert.net/), [Supabase pgvector](https://supabase.com/docs/guides/database/extensions/pgvector), and [OpenStreetMap](https://www.openstreetmap.org/) Kigali data.
