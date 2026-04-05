"""
hybrid_search.py
================
Combines TF-IDF and embedding scores into one final ranked result.

Formula:
  final_score = alpha * tfidf_score + beta * embedding_score
  default: alpha=0.8, beta=0.2

Why hybrid:
  - TF-IDF is strong on exact Kinyarwanda keyword matches
  - Embeddings are strong on English and semantic meaning
  - Together they cover all three query types: RW, EN, and mixed

This is the only file the rest of the system (API, demo UI,
Next.js integration) needs to call.

Author : NIYIBIZI Prince
Project: kinyarwanda-search
"""

from preprocessor        import preprocess
import tfidf_retriever     as tfidf
import embedding_retriever as embed

# ---------------------------------------------------------------------------
# Fusion weights
# alpha + beta should always equal 1.0
# These will be tuned in Phase 3 using MRR evaluation
# ---------------------------------------------------------------------------
DEFAULT_ALPHA = 0.8   # weight for TF-IDF score
DEFAULT_BETA  = 0.2   # weight for embedding score


# ---------------------------------------------------------------------------
# Core hybrid search function
# ---------------------------------------------------------------------------

def search(
    query   : str,
    top_k   : int   = 10,
    alpha   : float = DEFAULT_ALPHA,
    beta    : float = DEFAULT_BETA,
) -> dict:
    """
    Run hybrid search over the product catalog.

    Steps:
      1. Preprocess the query
      2. Get top-N results from TF-IDF retriever
      3. Get top-N results from embedding retriever
      4. Merge both result sets by product id
      5. Compute hybrid score for every product
      6. Return top_k products ranked by hybrid score

    Args:
      query   : raw search query (any language)
      top_k   : number of final results to return
      alpha   : weight for TF-IDF score  (default 0.4)
      beta    : weight for embedding score (default 0.6)

    Returns a dict with:
      - query_info : preprocessed query details
      - results    : ranked list of products with all three scores
      - weights    : the alpha/beta values used
    """

    # Step 1 — preprocess
    query_info = preprocess(query)

    # Step 2 — retrieve from both systems
    # fetch more than top_k so the merge has enough candidates
    fetch_k = max(top_k * 2, 20)

    tfidf_results = tfidf.search(query, top_k=fetch_k)
    embed_results = embed.search(query, top_k=fetch_k)

    # Step 3 — build score maps keyed by product id
    tfidf_scores = {
        r["id"]: r["tfidf_score"]
        for r in tfidf_results
    }
    embed_scores = {
        r["id"]: r["embedding_score"]
        for r in embed_results
    }

    # Step 4 — collect all unique product ids from both lists
    all_ids = set(tfidf_scores.keys()) | set(embed_scores.keys())

    # Build a product lookup from both result sets
    product_lookup = {}
    for r in tfidf_results + embed_results:
        if r["id"] not in product_lookup:
            product_lookup[r["id"]] = r

    # Step 5 — compute hybrid score for every candidate
    scored = []
    for pid in all_ids:
        t_score = tfidf_scores.get(pid, 0.0)
        e_score = embed_scores.get(pid, 0.0)
        h_score = alpha * t_score + beta * e_score

        product = product_lookup[pid].copy()

        # Clean up retriever-specific rank fields
        product.pop("rank", None)
        product.pop("tfidf_score",     None)
        product.pop("embedding_score", None)

        product["tfidf_score"]     = round(t_score, 4)
        product["embedding_score"] = round(e_score, 4)
        product["hybrid_score"]    = round(h_score, 4)

        scored.append(product)

    # Step 6 — sort by hybrid score descending
    scored.sort(key=lambda x: x["hybrid_score"], reverse=True)
    top_results = scored[:top_k]

    # Add final rank
    for i, r in enumerate(top_results, start=1):
        r["rank"] = i

    return {
        "query_info": query_info,
        "results"   : top_results,
        "weights"   : {"alpha": alpha, "beta": beta},
    }


def format_results(response: dict) -> None:
    """
    Pretty-print hybrid search results to the terminal.
    Used for testing and debugging.
    """
    q    = response["query_info"]
    w    = response["weights"]
    res  = response["results"]

    print(f"\nQuery    : {q['original']}")
    print(f"Cleaned  : {q['cleaned']}")
    print(f"Language : {q['language']}")
    print(f"Weights  : TF-IDF={w['alpha']}  Embedding={w['beta']}")
    print(f"Results  : {len(res)} products")
    print("-" * 72)
    print(f"{'Rk':<4} {'Hybrid':<8} {'TF-IDF':<8} {'Embed':<8} {'Name'}")
    print("-" * 72)
    for r in res:
        print(
            f"  {r['rank']:<3}"
            f" {r['hybrid_score']:<8}"
            f" {r['tfidf_score']:<8}"
            f" {r['embedding_score']:<8}"
            f" {r['name']}"
        )


# ---------------------------------------------------------------------------
# Quick test
# Usage: python search/hybrid_search.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    test_queries = [
        # The three language patterns
        "ndashaka telefoni nziza",
        "best laptop for students",
        "ndashaka laptop nziza kuri school",
        # Specific product queries
        "agaseke ka mudasobwa waterproof",
        "losyo y'umubiri",
        "samsung smart TV",
        "impuzu nziza za running",
        "igitanda kinini",
    ]

    print("Hybrid Search Test")
    print("=" * 72)

    for q in test_queries:
        response = search(q, top_k=3)
        format_results(response)