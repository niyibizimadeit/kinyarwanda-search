"""
tfidf_retriever.py
==================
Builds and queries a bilingual TF-IDF index over the product catalog.

The index is built on the `search_text` field of each product, which
contains English name + Kinyarwanda name + English description +
Kinyarwanda description + category all in one string.

This means one index searches both languages simultaneously — no
translation or language separation needed.

Two modes:
  1. Build  — reads products.json, builds index, saves to data/processed/
  2. Search — loads saved index, scores a query, returns ranked products

Author : NIYIBIZI Prince
Project: kinyarwanda-search
"""

import json
import pickle
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from preprocessor import preprocess

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR       = Path(__file__).parent.parent
PRODUCTS_PATH  = BASE_DIR / "data" / "raw"      / "products.json"
PROCESSED_DIR  = BASE_DIR / "data" / "processed"
VECTORIZER_PATH = PROCESSED_DIR / "tfidf_vectorizer.pkl"
MATRIX_PATH     = PROCESSED_DIR / "tfidf_matrix.pkl"
PRODUCTS_CACHE  = PROCESSED_DIR / "products_cache.pkl"


# ---------------------------------------------------------------------------
# BUILD — run once to create the index
# ---------------------------------------------------------------------------

def build_index() -> None:
    """
    Read all products, build the TF-IDF index, save to disk.

    What gets saved:
      - tfidf_vectorizer.pkl  : the fitted TfidfVectorizer
                                (knows the full vocabulary + IDF scores)
      - tfidf_matrix.pkl      : product matrix, shape (n_products, n_features)
                                (every product as a numeric vector)
      - products_cache.pkl    : the product list in the same row order
                                (so we can map a row index back to a product)
    """
    print("Building TF-IDF index...")

    # Load products
    with open(PRODUCTS_PATH, encoding="utf-8") as f:
        products = json.load(f)

    print(f"  Loaded {len(products)} products")

    # Extract the search_text field from every product
    # This single field already contains EN + RW content
    corpus = [p["search_text"] for p in products]

    # Build the vectorizer
    # analyzer="word"      — treat individual words as features
    # ngram_range=(1, 2)   — also consider 2-word phrases
    #                         e.g. "telefoni nziza" as one feature
    #                         this improves matching for compound terms
    # min_df=1             — include a word even if it appears in only 1 product
    #                         important for rare Kinyarwanda terms
    # max_df=0.95          — ignore words that appear in >95% of products
    #                         these are too common to be useful signals
    # sublinear_tf=True    — dampen the effect of very high term frequencies
    #                         prevents one word repeated 50 times from dominating
    vectorizer = TfidfVectorizer(
        analyzer     = "word",
        ngram_range  = (1, 2),
        min_df       = 1,
        max_df       = 0.95,
        sublinear_tf = True,
    )

    # Fit and transform: learn vocabulary + convert all products to vectors
    tfidf_matrix = vectorizer.fit_transform(corpus)

    print(f"  Vocabulary size : {len(vectorizer.vocabulary_)} unique tokens")
    print(f"  Matrix shape    : {tfidf_matrix.shape} "
          f"({tfidf_matrix.shape[0]} products × {tfidf_matrix.shape[1]} features)")

    # Save everything to disk
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    with open(MATRIX_PATH, "wb") as f:
        pickle.dump(tfidf_matrix, f)

    with open(PRODUCTS_CACHE, "wb") as f:
        pickle.dump(products, f)

    print(f"  Saved index to {PROCESSED_DIR}/")
    print("Done. Index is ready for search.")


# ---------------------------------------------------------------------------
# SEARCH — run on every query
# ---------------------------------------------------------------------------

def load_index():
    """
    Load the saved TF-IDF index from disk.
    Returns (vectorizer, tfidf_matrix, products).
    Raises FileNotFoundError if build_index() has not been run yet.
    """
    if not VECTORIZER_PATH.exists():
        raise FileNotFoundError(
            "TF-IDF index not found. Run build_index() first.\n"
            "  python search/tfidf_retriever.py --build"
        )

    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)

    with open(MATRIX_PATH, "rb") as f:
        tfidf_matrix = pickle.load(f)

    with open(PRODUCTS_CACHE, "rb") as f:
        products = pickle.load(f)

    return vectorizer, tfidf_matrix, products


def search(query: str, top_k: int = 10) -> list:
    """
    Search the TF-IDF index for a given query.

    Steps:
      1. Preprocess the query (clean + tokenize)
      2. Convert query to a TF-IDF vector using the saved vectorizer
      3. Compute cosine similarity between query vector and all product vectors
      4. Return top_k products ranked by score

    Args:
      query  : raw search query (any language, any case, any punctuation)
      top_k  : number of results to return (default 10)

    Returns:
      List of dicts, each containing the product fields plus:
        - tfidf_score : float between 0 and 1 (higher = more relevant)
        - rank        : position in results (1 = best)
    """
    vectorizer, tfidf_matrix, products = load_index()

    # Preprocess the query
    processed = preprocess(query)
    cleaned   = processed["cleaned"]

    # Convert query to TF-IDF vector
    # transform() uses the vocabulary learned during build_index()
    # unknown words (not seen during build) are silently ignored
    query_vector = vectorizer.transform([cleaned])

    # Compute cosine similarity between query and every product
    # Result shape: (1, n_products)
    scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # Get indices of top_k highest scores
    top_indices = np.argsort(scores)[::-1][:top_k]

    # Build result list
    results = []
    for rank, idx in enumerate(top_indices, start=1):
        score = float(scores[idx])
        if score == 0:
            break  # remaining results have zero relevance
        product = products[idx].copy()
        product["tfidf_score"] = round(score, 4)
        product["rank"]        = rank
        results.append(product)

    return results


# ---------------------------------------------------------------------------
# Quick test — run this file directly
# Usage:
#   python search/tfidf_retriever.py --build     (build the index)
#   python search/tfidf_retriever.py             (run test searches)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if "--build" in sys.argv:
        build_index()
        sys.exit(0)

    # Test searches — covers all three language patterns
    test_queries = [
        "ndashaka telefoni nziza",           # Full Kinyarwanda
        "best laptop for students",           # Full English
        "ndashaka laptop nziza kuri school",  # Mixed
        "agaseke ka mudasobwa waterproof",    # Mixed — bag for laptop
        "losyo y'umubiri",                    # Kinyarwanda — body lotion
        "samsung smart TV",                   # English — electronics
        "impuzu nziza za running",            # Mixed — running clothes
        "igitanda kinini",                    # Kinyarwanda — big bed
    ]

    print("TF-IDF Retriever Test")
    print("=" * 60)

    for q in test_queries:
        results = search(q, top_k=3)
        lang    = preprocess(q)["language"]
        print(f"\nQuery [{lang}]: {q}")
        print(f"{'Rank':<6} {'Score':<8} {'Name'}")
        print("-" * 55)
        if results:
            for r in results:
                print(f"  {r['rank']:<4} {r['tfidf_score']:<8} {r['name']}")
        else:
            print("  No results found")