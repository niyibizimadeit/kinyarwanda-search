"""
evaluate.py
===========
Measures search engine quality using two standard IR metrics:
  - MRR   (Mean Reciprocal Rank)
  - NDCG@5 (Normalized Discounted Cumulative Gain at 5)

Runs evaluation across three modes:
  1. TF-IDF only
  2. Embeddings only
  3. Hybrid (alpha=0.4, beta=0.6)

Also tests different alpha/beta weight combinations to find
the best performing hybrid configuration.

Results are printed to the terminal and saved to:
  data/processed/evaluation_results.json

Author : NIYIBIZI Prince
Project: kinyarwanda-search
"""

import json
import math
import sys
import os
import warnings
from pathlib import Path

# Suppress noisy HuggingFace warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")

# Add search/ to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "search"))

import tfidf_retriever     as tfidf
import embedding_retriever as embed
from hybrid_search import search as hybrid_search
from preprocessor  import preprocess

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR      = Path(__file__).parent
LABELS_PATH   = BASE_DIR / "data" / "raw"       / "query_labels.json"
RESULTS_PATH  = BASE_DIR / "data" / "processed" / "evaluation_results.json"


# ---------------------------------------------------------------------------
# Metric functions
# ---------------------------------------------------------------------------

def reciprocal_rank(results: list, relevant_name: str) -> float:
    """
    Compute the Reciprocal Rank for one query.

    If the relevant product appears at rank k, RR = 1/k.
    If it does not appear in the results, RR = 0.

    Args:
      results       : list of result dicts with a 'name' field
      relevant_name : the correct product name for this query

    Returns:
      float between 0 and 1
    """
    for i, result in enumerate(results, start=1):
        if result["name"].strip().lower() == relevant_name.strip().lower():
            return 1.0 / i
    return 0.0


def dcg_at_k(results: list, relevant_name: str, k: int = 5) -> float:
    """
    Compute Discounted Cumulative Gain at k.

    Assigns relevance 1 to the correct product, 0 to all others.
    Discounts by log2(rank + 1).

    DCG@k = sum over top-k results of: rel_i / log2(i + 1)
    """
    dcg = 0.0
    for i, result in enumerate(results[:k], start=1):
        if result["name"].strip().lower() == relevant_name.strip().lower():
            dcg += 1.0 / math.log2(i + 1)
    return dcg


def ndcg_at_k(results: list, relevant_name: str, k: int = 5) -> float:
    """
    Compute Normalized DCG at k.

    NDCG = DCG / IDCG
    where IDCG is the ideal DCG (relevant product at rank 1).

    IDCG = 1 / log2(1 + 1) = 1 / 1 = 1.0

    So NDCG@k = DCG@k for binary relevance with one relevant document.
    """
    idcg = 1.0 / math.log2(2)   # ideal: relevant product at rank 1
    dcg  = dcg_at_k(results, relevant_name, k)
    return dcg / idcg if idcg > 0 else 0.0


# ---------------------------------------------------------------------------
# Retrieval wrappers
# ---------------------------------------------------------------------------

def search_tfidf(query: str, top_k: int = 10) -> list:
    return tfidf.search(query, top_k=top_k)


def search_embedding(query: str, top_k: int = 10) -> list:
    return embed.search(query, top_k=top_k)


def search_hybrid(query: str, top_k: int = 10,
                  alpha: float = 0.4, beta: float = 0.6) -> list:
    response = hybrid_search(query, top_k=top_k, alpha=alpha, beta=beta)
    return response["results"]


# ---------------------------------------------------------------------------
# Evaluation runner
# ---------------------------------------------------------------------------

def evaluate_mode(labels: list, mode: str,
                  alpha: float = 0.4, beta: float = 0.6,
                  top_k: int = 10) -> dict:
    """
    Run evaluation for one retrieval mode across all labeled queries.

    Args:
      labels : list of query label dicts
      mode   : "tfidf", "embedding", or "hybrid"
      alpha  : TF-IDF weight (hybrid only)
      beta   : embedding weight (hybrid only)
      top_k  : number of results to retrieve

    Returns dict with:
      - mrr        : Mean Reciprocal Rank
      - ndcg_5     : Mean NDCG@5
      - per_query  : per-query breakdown
      - by_language: MRR broken down by language (rw / en / mixed)
    """
    rr_scores   = []
    ndcg_scores = []
    per_query   = []

    # Track scores by language
    lang_scores = {"rw": [], "en": [], "mixed": []}

    for label in labels:
        query    = label["query"]
        relevant = label["relevant_product_name"]
        lang     = label["language"]

        # Get results from the appropriate retriever
        if mode == "tfidf":
            results = search_tfidf(query, top_k=top_k)
        elif mode == "embedding":
            results = search_embedding(query, top_k=top_k)
        else:
            results = search_hybrid(query, top_k=top_k,
                                    alpha=alpha, beta=beta)

        # Compute metrics
        rr   = reciprocal_rank(results, relevant)
        ndcg = ndcg_at_k(results, relevant, k=5)

        rr_scores.append(rr)
        ndcg_scores.append(ndcg)
        lang_scores[lang].append(rr)

        # Find where the correct answer landed
        rank_found = None
        for i, r in enumerate(results, start=1):
            if r["name"].strip().lower() == relevant.strip().lower():
                rank_found = i
                break

        per_query.append({
            "query"    : query,
            "language" : lang,
            "relevant" : relevant,
            "rank"     : rank_found,
            "rr"       : round(rr, 4),
            "ndcg_5"   : round(ndcg, 4),
            "found"    : rank_found is not None,
        })

    # Aggregate
    mrr       = sum(rr_scores)   / len(rr_scores)
    mean_ndcg = sum(ndcg_scores) / len(ndcg_scores)

    by_language = {}
    for lang, scores in lang_scores.items():
        by_language[lang] = round(sum(scores) / len(scores), 4) if scores else 0.0

    return {
        "mrr"        : round(mrr, 4),
        "ndcg_5"     : round(mean_ndcg, 4),
        "by_language": by_language,
        "per_query"  : per_query,
    }


# ---------------------------------------------------------------------------
# Weight tuning
# ---------------------------------------------------------------------------

def tune_weights(labels: list) -> dict:
    """
    Try different alpha/beta combinations and find the best MRR.

    Tests alpha values from 0.1 to 0.9 in steps of 0.1.
    beta = 1 - alpha always.

    Returns the best (alpha, beta, mrr) combination.
    """
    print("\nTuning alpha/beta weights...")
    print(f"  {'Alpha':<8} {'Beta':<8} {'MRR':<8} {'NDCG@5'}")
    print("  " + "-" * 36)

    best = {"alpha": 0.4, "beta": 0.6, "mrr": 0.0, "ndcg_5": 0.0}
    tuning_results = []

    for alpha_10 in range(1, 10):  # 0.1 to 0.9
        alpha = alpha_10 / 10
        beta  = round(1.0 - alpha, 1)

        result = evaluate_mode(labels, "hybrid", alpha=alpha, beta=beta)
        mrr    = result["mrr"]
        ndcg   = result["ndcg_5"]

        marker = " ← best" if mrr > best["mrr"] else ""
        print(f"  {alpha:<8} {beta:<8} {mrr:<8} {ndcg}{marker}")

        tuning_results.append({
            "alpha" : alpha,
            "beta"  : beta,
            "mrr"   : mrr,
            "ndcg_5": ndcg,
        })

        if mrr > best["mrr"]:
            best = {"alpha": alpha, "beta": beta,
                    "mrr": mrr, "ndcg_5": ndcg}

    return best, tuning_results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\nKinyarwanda-English Search Engine — Evaluation")
    print("=" * 60)

    # Load labels
    with open(LABELS_PATH, encoding="utf-8") as f:
        labels = json.load(f)
    print(f"Loaded {len(labels)} labeled queries")
    print(f"  RW: {sum(1 for l in labels if l['language']=='rw')}  "
          f"EN: {sum(1 for l in labels if l['language']=='en')}  "
          f"Mixed: {sum(1 for l in labels if l['language']=='mixed')}")

    # ---------------------
    # Run all three modes
    # ---------------------
    print("\nRunning evaluation across all three modes...")

    print("  [1/3] TF-IDF only...")
    tfidf_results = evaluate_mode(labels, "tfidf")

    print("  [2/3] Embeddings only...")
    embed_results = evaluate_mode(labels, "embedding")

    print("  [3/3] Hybrid (alpha=0.4, beta=0.6)...")
    hybrid_results = evaluate_mode(labels, "hybrid")

    # ---------------------
    # Print comparison table
    # ---------------------
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"{'Mode':<20} {'MRR':<10} {'NDCG@5':<10}")
    print("-" * 40)
    print(f"{'TF-IDF only':<20} {tfidf_results['mrr']:<10} {tfidf_results['ndcg_5']:<10}")
    print(f"{'Embeddings only':<20} {embed_results['mrr']:<10} {embed_results['ndcg_5']:<10}")
    print(f"{'Hybrid (0.4/0.6)':<20} {hybrid_results['mrr']:<10} {hybrid_results['ndcg_5']:<10}")

    print("\nMRR BY LANGUAGE")
    print("-" * 40)
    print(f"{'Mode':<20} {'RW':<10} {'EN':<10} {'Mixed':<10}")
    print("-" * 40)
    for mode_name, res in [
        ("TF-IDF", tfidf_results),
        ("Embeddings", embed_results),
        ("Hybrid", hybrid_results),
    ]:
        bl = res["by_language"]
        print(f"{mode_name:<20} {bl['rw']:<10} {bl['en']:<10} {bl['mixed']:<10}")

    # ---------------------
    # Tune weights
    # ---------------------
    best, tuning = tune_weights(labels)

    print(f"\nBest weights: alpha={best['alpha']}, beta={best['beta']}")
    print(f"Best MRR    : {best['mrr']}")
    print(f"Best NDCG@5 : {best['ndcg_5']}")

    # ---------------------
    # Show failure cases
    # ---------------------
    print("\nFAILURE CASES (correct product not found in top 10)")
    print("-" * 60)
    failures = [q for q in hybrid_results["per_query"] if not q["found"]]
    if failures:
        for f in failures:
            print(f"  [{f['language']}] {f['query']}")
            print(f"         Expected: {f['relevant']}")
    else:
        print("  None — all queries returned the correct product in top 10")

    print("\nWEAK RESULTS (correct product found but not at rank 1)")
    print("-" * 60)
    weak = [q for q in hybrid_results["per_query"]
            if q["found"] and q["rank"] and q["rank"] > 1]
    for w in weak[:10]:   # show top 10 weak results
        print(f"  [{w['language']}] {w['query']}")
        print(f"         Expected rank 1 — found at rank {w['rank']}")

    # ---------------------
    # Save results
    # ---------------------
    output = {
        "summary": {
            "tfidf"   : {"mrr": tfidf_results["mrr"],  "ndcg_5": tfidf_results["ndcg_5"]},
            "embedding": {"mrr": embed_results["mrr"],  "ndcg_5": embed_results["ndcg_5"]},
            "hybrid"  : {"mrr": hybrid_results["mrr"], "ndcg_5": hybrid_results["ndcg_5"]},
        },
        "by_language": {
            "tfidf"    : tfidf_results["by_language"],
            "embedding": embed_results["by_language"],
            "hybrid"   : hybrid_results["by_language"],
        },
        "best_weights" : best,
        "tuning"       : tuning,
        "failure_cases": failures,
        "weak_cases"   : weak,
        "per_query"    : {
            "tfidf"    : tfidf_results["per_query"],
            "embedding": embed_results["per_query"],
            "hybrid"   : hybrid_results["per_query"],
        },
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nFull results saved to {RESULTS_PATH}")
    print("\nNext step: update the README evaluation table with these numbers.")


if __name__ == "__main__":
    main()