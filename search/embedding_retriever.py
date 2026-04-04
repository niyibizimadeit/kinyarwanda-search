"""
embedding_retriever.py
======================
Builds and queries a multilingual sentence embedding index.

Uses paraphrase-multilingual-MiniLM-L12-v2 — a lightweight model
trained on 50+ languages that understands semantic similarity across
languages, meaning "telefoni" and "phone" end up close together
in the 512-dimensional embedding space.

Two modes:
  1. Build  — encodes all products, saves embeddings to disk
  2. Search — encodes a query, finds nearest product embeddings

Author : NIYIBIZI Prince
Project: kinyarwanda-search
"""

import json
import pickle
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from preprocessor import preprocess

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR         = Path(__file__).parent.parent
PRODUCTS_PATH    = BASE_DIR / "data" / "raw"       / "products.json"
PROCESSED_DIR    = BASE_DIR / "data" / "processed"
EMBEDDINGS_PATH  = PROCESSED_DIR / "embeddings.npy"
PRODUCTS_CACHE   = PROCESSED_DIR / "products_cache.pkl"

# The model name — lightweight (470MB), supports 50+ languages
# including languages close to Kinyarwanda
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


# ---------------------------------------------------------------------------
# BUILD — run once to encode all products
# ---------------------------------------------------------------------------

def build_embeddings() -> None:
    """
    Load all products, encode their search_text into 512-dim vectors,
    and save the embedding matrix to disk.

    What gets saved:
      - embeddings.npy     : numpy array of shape (n_products, 512)
                             one row per product
      - products_cache.pkl : product list in the same row order
                             (shared with tfidf_retriever)
    """
    print("Building embedding index...")
    print(f"  Loading model: {MODEL_NAME}")
    print("  (first run downloads ~470MB — subsequent runs load from cache)\n")

    # Load the multilingual model
    # Downloads once, cached in ~/.cache/torch/sentence_transformers/
    model = SentenceTransformer(MODEL_NAME)

    # Load products
    with open(PRODUCTS_PATH, encoding="utf-8") as f:
        products = json.load(f)

    print(f"  Loaded {len(products)} products")

    # Extract search_text from every product
    # This field contains EN + RW content combined
    corpus = [p["search_text"] for p in products]

    # Encode all products into 512-dimensional vectors
    # show_progress_bar=True prints a progress bar during encoding
    # batch_size=32 processes 32 products at a time (memory efficient)
    print("  Encoding products...")
    embeddings = model.encode(
        corpus,
        show_progress_bar = True,
        batch_size        = 32,
        normalize_embeddings = True,  # normalize to unit length
                                      # makes cosine similarity = dot product
                                      # which is faster to compute
    )

    print(f"\n  Embedding matrix shape: {embeddings.shape}")
    print(f"  ({embeddings.shape[0]} products × {embeddings.shape[1]} dimensions)")

    # Save to disk
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    np.save(EMBEDDINGS_PATH, embeddings)

    # Save products cache (same order as embeddings)
    with open(PRODUCTS_CACHE, "wb") as f:
        pickle.dump(products, f)

    print(f"\n  Saved embeddings to {EMBEDDINGS_PATH}")
    print("Done. Embedding index is ready for search.")


# ---------------------------------------------------------------------------
# SEARCH — run on every query
# ---------------------------------------------------------------------------

def load_embeddings():
    """
    Load saved embeddings and products from disk.
    Returns (embeddings, products).
    """
    if not EMBEDDINGS_PATH.exists():
        raise FileNotFoundError(
            "Embeddings not found. Run build_embeddings() first.\n"
            "  python search/embedding_retriever.py --build"
        )

    embeddings = np.load(EMBEDDINGS_PATH)

    with open(PRODUCTS_CACHE, "rb") as f:
        products = pickle.load(f)

    return embeddings, products


# Keep the model in memory after first load
# so we don't reload it on every search call
_model_cache = None

def get_model() -> SentenceTransformer:
    """Load and cache the sentence transformer model."""
    global _model_cache
    if _model_cache is None:
        _model_cache = SentenceTransformer(MODEL_NAME)
    return _model_cache


def search(query: str, top_k: int = 10) -> list:
    """
    Search the embedding index for a given query.

    Steps:
      1. Preprocess the query
      2. Encode the query into a 512-dim vector
      3. Compute cosine similarity with all product embeddings
      4. Return top_k products ranked by similarity

    Args:
      query  : raw search query (any language, any case)
      top_k  : number of results to return (default 10)

    Returns:
      List of dicts, each containing product fields plus:
        - embedding_score : float between 0 and 1
        - rank            : position in results (1 = best)
    """
    embeddings, products = load_embeddings()
    model                = get_model()

    # Preprocess query
    processed = preprocess(query)
    cleaned   = processed["cleaned"]

    # Encode query into a 512-dim vector
    query_embedding = model.encode(
        [cleaned],
        normalize_embeddings = True,
    )

    # Compute cosine similarity between query and all products
    scores = cosine_similarity(query_embedding, embeddings).flatten()

    # Get top_k indices sorted by score descending
    top_indices = np.argsort(scores)[::-1][:top_k]

    # Build result list
    results = []
    for rank, idx in enumerate(top_indices, start=1):
        score = float(scores[idx])
        product = products[idx].copy()
        product["embedding_score"] = round(score, 4)
        product["rank"]            = rank
        results.append(product)

    return results


# ---------------------------------------------------------------------------
# Quick test
# Usage:
#   python search/embedding_retriever.py --build    (encode all products)
#   python search/embedding_retriever.py            (run test searches)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if "--build" in sys.argv:
        build_embeddings()
        sys.exit(0)

    # Test searches — same queries as tfidf_retriever for easy comparison
    test_queries = [
        "ndashaka telefoni nziza",
        "best laptop for students",
        "ndashaka laptop nziza kuri school",
        "agaseke ka mudasobwa waterproof",
        "losyo y'umubiri",
        "samsung smart TV",
        "impuzu nziza za running",
        "igitanda kinini",
    ]

    print("Embedding Retriever Test")
    print("=" * 60)

    for q in test_queries:
        results = search(q, top_k=3)
        lang    = preprocess(q)["language"]
        print(f"\nQuery [{lang}]: {q}")
        print(f"{'Rank':<6} {'Score':<8} {'Name'}")
        print("-" * 55)
        for r in results:
            print(f"  {r['rank']:<4} {r['embedding_score']:<8} {r['name']}")