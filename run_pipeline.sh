#!/usr/bin/env bash
# run_pipeline.sh — APT Taxonomy full pipeline runner
# Usage:
#   bash run_pipeline.sh                 # full pipeline (scrape → clean → cluster)
#   bash run_pipeline.sh --taxonomy-only # skip scraping, use existing CSVs
#   bash run_pipeline.sh --web           # start the Flask web interface

set -euo pipefail

TAXONOMY_ONLY=false
WEB_MODE=false

for arg in "$@"; do
  case $arg in
    --taxonomy-only) TAXONOMY_ONLY=true ;;
    --web)           WEB_MODE=true ;;
  esac
done

echo "=================================================="
echo "  APT Taxonomy Intelligence Pipeline"
echo "=================================================="

# ── Web mode ──────────────────────────────────────────
if $WEB_MODE; then
  echo ""
  echo "Starting Flask web interface..."
  pip install flask --quiet
  python app.py
  exit 0
fi

# ── Dependency check ──────────────────────────────────
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
python -c "import nltk; nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('omw-1.4', quiet=True)"

# ── Stage 1 — Scraper ─────────────────────────────────
if ! $TAXONOMY_ONLY; then
  echo ""
  echo "Stage 1: Scraping papers from Semantic Scholar API (~15 min)..."
  python scraper.py
else
  echo ""
  echo "Skipping Stage 1 (--taxonomy-only). Using existing apt_papers_raw.csv"
fi

# ── Stage 2 — Preprocessing ───────────────────────────
echo ""
echo "Stage 2: NLP preprocessing (~1 min)..."
python preprocess.py

# ── Stage 3 — Taxonomy builder ────────────────────────
echo ""
echo "Stage 3: Hierarchical clustering + labeling (~3 min, first run downloads ~1.1 GB model)..."
python taxonomy_builder.py

echo ""
echo "=================================================="
echo "  Pipeline complete. Outputs:"
echo "  • apt_papers_raw.csv         (scraped papers)"
echo "  • apt_papers_clean.csv       (cleaned corpus)"
echo "  • final_taxonomy_mapping.csv (taxonomy output)"
echo "  • apt_dendrogram.png         (Ward dendrogram)"
echo "  • apt_taxonomy_tree.png      (hierarchy tree)"
echo "  • silhouette_scores.png      (k validation)"
echo "  • corpus_distribution.png   (year distribution)"
echo ""
echo "  To explore results interactively:"
echo "  bash run_pipeline.sh --web"
echo "=================================================="
