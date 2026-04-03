"""
preprocessor.py
===============
Cleans and analyzes incoming search queries before they reach
the TF-IDF or embedding retriever.

What it does:
  1. Lowercases the query
  2. Removes punctuation and extra whitespace
  3. Detects whether the query is English, Kinyarwanda, or mixed

Author : NIYIBIZI Prince
Project: kinyarwanda-search
"""

import re
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Load the Kinyarwanda vocabulary lexicon we generated in Phase 1.
# This is used to detect which language a query is written in.
# ---------------------------------------------------------------------------

LEXICON_PATH = Path(__file__).parent.parent / "data" / "raw" / "lexicon.json"

def _load_kinyarwanda_words() -> set:
    """
    Build a set of all Kinyarwanda words from the lexicon.
    Used for language detection.
    """
    if not LEXICON_PATH.exists():
        # Fallback: hardcoded core words if lexicon file not found
        return {
            "ndashaka", "igiciro", "nziza", "kugura", "ibicuruzwa",
            "gutumiza", "amafaranga", "telefoni", "mudasobwa", "televiziyo",
            "isafuriya", "intebe", "igitanda", "losyo", "kremu", "impuzu",
            "urukweto", "agaseke", "bateri", "chajilo", "insinga", "ecran",
            "umubiri", "imisatsi", "parefumu", "shampoo", "isabuni", "mesa",
            "garderobe", "matelas", "sofa", "etagere", "bureau", "robe",
            "chemise", "pantalon", "ijaki", "kitenge", "saa", "kamera",
            "ventilateu", "blender", "bouilloire", "frigo", "amashanyarazi",
            "uruhu", "amavuta", "ibara", "ingano", "gishya", "ubwiza",
        }

    with open(LEXICON_PATH, encoding="utf-8") as f:
        lexicon = json.load(f)

    words = set()
    for entry in lexicon:
        # Add the Kinyarwanda word itself
        rw_word = entry["kinyarwanda"].lower().strip()
        words.add(rw_word)
        # Also add individual tokens from multi-word entries
        # e.g. "amavuta y'imisatsi" → {"amavuta", "y'imisatsi"}
        for token in rw_word.split():
            words.add(token)
        # Add tokens from the example sentence too
        example = entry.get("example", "").lower()
        for token in example.split():
            clean = re.sub(r"[^\w]", "", token)
            if clean:
                words.add(clean)

    return words


# Build the word set once when the module is imported
KINYARWANDA_WORDS = _load_kinyarwanda_words()

# Common English stop words — used to help with language detection
ENGLISH_WORDS = {
    "the", "a", "an", "and", "or", "for", "with", "in", "of", "to",
    "is", "are", "was", "it", "this", "that", "best", "good", "new",
    "buy", "price", "cheap", "sale", "size", "color", "set", "pack",
    "inch", "liter", "watt", "men", "women", "boys", "girls", "large",
    "small", "slim", "fit", "fast", "high", "low", "long", "short",
    "white", "black", "blue", "red", "grey", "green", "portable",
    "wireless", "electric", "digital", "smart", "professional",
}


# ---------------------------------------------------------------------------
# Core preprocessing functions
# ---------------------------------------------------------------------------

def clean_query(query: str) -> str:
    """
    Clean a raw search query.

    Steps:
      - Strip leading/trailing whitespace
      - Lowercase everything
      - Remove punctuation except apostrophes (important for Kinyarwanda
        words like "y'imisatsi" or "k'umugore")
      - Collapse multiple spaces into one

    Examples:
      "Ndashaka TELEFONI Nziza!!"  →  "ndashaka telefoni nziza"
      "phone case (Samsung)"       →  "phone case samsung"
      "losyo y'umubiri"            →  "losyo y'umubiri"
    """
    query = query.strip().lower()

    # Keep letters, digits, spaces, and apostrophes (for Kinyarwanda)
    query = re.sub(r"[^\w\s']", " ", query)

    # Collapse multiple spaces
    query = re.sub(r"\s+", " ", query).strip()

    return query


def tokenize(query: str) -> list:
    """
    Split a cleaned query into individual tokens (words).

    Example:
      "ndashaka telefoni nziza"  →  ["ndashaka", "telefoni", "nziza"]
    """
    return query.split()


def detect_language(query: str) -> str:
    """
    Detect whether a query is Kinyarwanda, English, or mixed.

    Method:
      - Tokenize the cleaned query
      - Count how many tokens appear in the Kinyarwanda word set
      - Count how many tokens appear in the English word set
      - Classify based on the ratio

    Returns:
      "rw"    — mostly or fully Kinyarwanda
      "en"    — mostly or fully English
      "mixed" — significant presence of both languages

    Examples:
      "ndashaka telefoni nziza"          →  "rw"
      "best laptop for university"       →  "en"
      "ndashaka laptop nziza kuri school" →  "mixed"
    """
    cleaned = clean_query(query)
    tokens  = tokenize(cleaned)

    if not tokens:
        return "en"

    rw_count = sum(1 for t in tokens if t in KINYARWANDA_WORDS)
    en_count = sum(1 for t in tokens if t in ENGLISH_WORDS)
    total    = len(tokens)

    rw_ratio = rw_count / total
    en_ratio = en_count / total

    # Classification thresholds
    if rw_ratio >= 0.5 and en_ratio < 0.2:
        return "rw"
    elif en_ratio >= 0.5 and rw_ratio < 0.2:
        return "en"
    elif rw_ratio > 0 and en_ratio > 0:
        return "mixed"
    elif rw_ratio >= 0.3:
        return "rw"
    else:
        return "en"


def preprocess(query: str) -> dict:
    """
    Full preprocessing pipeline — the single function the rest
    of the search engine calls.

    Returns a dict with:
      - original  : the raw query as typed
      - cleaned   : lowercased, punctuation removed
      - tokens    : list of individual words
      - language  : "rw", "en", or "mixed"
      - token_count: number of tokens

    Example:
      preprocess("Ndashaka laptop NZIZA kuri school!")
      →  {
           "original"    : "Ndashaka laptop NZIZA kuri school!",
           "cleaned"     : "ndashaka laptop nziza kuri school",
           "tokens"      : ["ndashaka", "laptop", "nziza", "kuri", "school"],
           "language"    : "mixed",
           "token_count" : 5
         }
    """
    cleaned  = clean_query(query)
    tokens   = tokenize(cleaned)
    language = detect_language(query)

    return {
        "original"    : query,
        "cleaned"     : cleaned,
        "tokens"      : tokens,
        "language"    : language,
        "token_count" : len(tokens),
    }


# ---------------------------------------------------------------------------
# Quick test — run this file directly to verify it works
# Usage: python search/preprocessor.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    test_queries = [
        "Ndashaka TELEFONI Nziza!!",
        "best laptop for university students",
        "ndashaka laptop nziza kuri school",
        "agaseke ka mudasobwa waterproof",
        "losyo y'umubiri ya Nivea",
        "igiciro cya iPhone 14 ni kangahe",
        "Samsung Smart TV 43 inch",
        "impuzu nziza za running",
    ]

    print("Preprocessor Test")
    print("=" * 60)

    for q in test_queries:
        result = preprocess(q)
        print(f"\nQuery    : {result['original']}")
        print(f"Cleaned  : {result['cleaned']}")
        print(f"Language : {result['language']}")
        print(f"Tokens   : {result['tokens']}")