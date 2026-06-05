# APT Taxonomy Intelligence

**A production-grade ML pipeline that automatically builds a hierarchical taxonomy of Advanced Persistent Threat research — and serves it as an interactive web application.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)](https://flask.palletsprojects.com)
[![sentence-transformers](https://img.shields.io/badge/sentence--transformers-2.7.0-orange)](https://www.sbert.net)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4.0-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![BITS Pilani](https://img.shields.io/badge/BITS_Pilani-CS_F266-0057A8)](https://bits-pilani.ac.in)

---

## What This Is

120 peer-reviewed APT security papers (2021–2026), automatically collected, cleaned, semantically embedded, and clustered into a 2-level taxonomy — then exposed as a searchable web interface and REST API.

**The problem it solves:** Threat intelligence analysts waste hours manually searching for relevant APT research. This pipeline organises the research landscape into a navigable structure, so finding papers on "lateral movement detection via provenance graphs" takes under 60 seconds instead of 30 minutes.

→ **[Live Demo](#running-the-web-interface)** | **[Product Thinking](PRODUCT_THINKING.md)** | **[JSON API](#api)**

---

## The Taxonomy Output

```
APT ATTACKS TAXONOMY  (120 papers · 2021–2026)
│
├── C1  Cyber Espionage & Nation-State Attribution          (n=18)
│   ├── S1  Attribution & Tracking                         (n=10)
│   └── S2  Forensic Investigation                         (n=8)
│
├── C2  ML-Based Intrusion Detection Systems               (n=22)
│   ├── S1  Detection & Classification                     (n=13)
│   └── S2  Behavioral Analysis                            (n=9)
│
├── C3  Malware Analysis & Reverse Engineering             (n=17)
│   ├── S1  Technique Analysis                             (n=9)
│   └── S2  Attribution & Tracking                        (n=8)
│
├── C4  Lateral Movement & C2 Infrastructure               (n=16)
│   ├── S1  Defense & Mitigation                           (n=8)
│   └── S2  Detection & Classification                     (n=8)
│
├── C5  Provenance Graphs & Attack Forensics               (n=19)
│   ├── S1  Forensic Investigation                         (n=11)
│   └── S2  Technique Analysis                             (n=8)
│
├── C6  Threat Intelligence & Kill Chain Modeling          (n=15)
│   ├── S1  Attribution & Tracking                         (n=8)
│   └── S2  Defense & Mitigation                           (n=7)
│
└── C7  Zero-Day Exploits & Vulnerability Analysis         (n=13)
    ├── S1  Detection & Classification                     (n=7)
    └── S2  Behavioral Analysis                            (n=6)
```

> Cluster labels are auto-assigned at runtime via Semantic Centroid Matching. The structure above reflects the actual output from running on the included corpus.

---

## Pipeline Architecture

```
┌──────────────────┐    ┌──────────────────┐    ┌─────────────────────────────┐
│   scraper.py     │───▶│  preprocess.py   │───▶│    taxonomy_builder.py      │
│                  │    │                  │    │                             │
│ Semantic Scholar │    │ HTML decode      │    │ Sentence-Transformer embed  │
│ 5 APT queries    │    │ URL removal      │    │ (all-mpnet-base-v2, 768-d)  │
│ Dual-group filter│    │ NLTK lemmatize   │    │ Ward HAC (Euclidean/L2)     │
│ 120 papers       │    │ Stop-word filter │    │ Semantic Centroid Matching  │
│ 2021–2026        │    │ Dual-group recheck│   │ Hungarian label assignment  │
└──────────────────┘    └──────────────────┘    └─────────────────────────────┘
         │                       │                            │
         ▼                       ▼                            ▼
apt_papers_raw.csv    apt_papers_clean.csv      final_taxonomy_mapping.csv
                                                apt_dendrogram.png
                                                apt_taxonomy_tree.png
                                                         │
                                                         ▼
                                              ┌──────────────────┐
                                              │     app.py       │
                                              │  Flask web UI    │
                                              │  + REST API      │
                                              └──────────────────┘
```

---

## Key Technical Decisions

### Why Ward Agglomerative Clustering?
K-Means produces flat buckets — not a taxonomy. HDBSCAN drops noise points, unacceptable for a small corpus. Ward HAC builds a full dendrogram, preserving the hierarchical structure at any depth.

### Why Semantic Centroid Matching instead of c-TF-IDF?
On 120 papers, c-TF-IDF labels are generic and repetitive — there isn't enough text mass per cluster for discriminative term frequency to emerge. Semantic Centroid Matching embeds both cluster centroids and expert-defined gold labels, then uses the Hungarian algorithm to find the globally optimal one-to-one assignment. The result: semantically coherent labels that reflect actual research focus, not just frequent words.

### Why `all-mpnet-base-v2` and not SecBERT?
SecBERT is a masked-LM BERT requiring custom mean-pooling with no validated sentence-level benchmarks for this task. `all-mpnet-base-v2` has strong sentence similarity performance and produces 768-dim L2-normalised vectors — making Ward's required Euclidean distance monotonic with cosine distance on the unit hypersphere. This trade-off is documented honestly in the code.

---

## Installation & Quick Start

```bash
# 1. Clone
git clone https://github.com/Kanik0575/apt-taxonomy-intelligence.git
cd apt-taxonomy-intelligence

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"

# 4. Optional: set Semantic Scholar API key
export SEMANTIC_SCHOLAR_API_KEY="your_key_here"
```

---

## Running the Pipeline

```bash
# Full pipeline (scrape → clean → cluster)  ~20 min total
bash run_pipeline.sh

# Skip scraping — use the included CSVs
bash run_pipeline.sh --taxonomy-only

# Individual stages
python scraper.py          # ~15 min  → apt_papers_raw.csv
python preprocess.py       # ~1 min   → apt_papers_clean.csv
python taxonomy_builder.py # ~3 min   → taxonomy outputs
```

---

## Running the Web Interface

```bash
pip install flask
python app.py
# Open http://localhost:5000
```

The web interface provides:
- **Home** — taxonomy overview, pipeline architecture, output visualisations
- **Search** — full-text search across all papers, filterable by year and cluster
- **Taxonomy** — collapsible cluster browser with sub-cluster tabs
- **Paper detail** — abstract, venue, related papers in same cluster, direct PDF link
- **JSON API** — programmatic access to the taxonomy

---

## API

```bash
# Search papers
GET /api/papers?q=lateral+movement&year=2023&limit=20

# Full taxonomy tree
GET /api/taxonomy

# Response format
{
  "total": 12,
  "papers": [
    {
      "paper_id": "...",
      "title": "...",
      "year": 2023,
      "authors": "...",
      "cluster_id": 4,
      "cluster_label": "Lateral Movement & Command-and-Control Infrastructure",
      "sub_id": 1,
      "sub_label": "Detection & Classification",
      "url": "https://..."
    }
  ]
}
```

---

## Output Files

| File | Description |
|------|-------------|
| `apt_papers_raw.csv` | 120 real papers from Semantic Scholar API |
| `apt_papers_clean.csv` | NLP-cleaned corpus after dual-group relevance filter |
| `final_taxonomy_mapping.csv` | **Main output:** every paper with cluster ID and semantic label |
| `apt_dendrogram.png` | Ward dendrogram with cluster-coloured branches |
| `apt_taxonomy_tree.png` | Hierarchy tree: Root → 7 clusters → 14 sub-clusters |
| `silhouette_scores.png` | Silhouette sweep validating k=7 |
| `corpus_distribution.png` | Papers per publication year |

---

## Repository Structure

```
apt-taxonomy-intelligence/
├── README.md                      ← This file
├── PRODUCT_THINKING.md            ← Product strategy & analyst UX design
├── requirements.txt               ← Python dependencies
├── run_pipeline.sh                ← One-command pipeline runner
│
├── scraper.py                     ← Stage 1: Semantic Scholar data collection
├── preprocess.py                  ← Stage 2: NLP cleaning pipeline
├── taxonomy_builder.py            ← Stage 3: Embedding, clustering, labeling
├── app.py                         ← Flask web application & REST API
│
├── templates/
│   ├── base.html                  ← Nav, footer, Tailwind CSS
│   ├── index.html                 ← Home: overview + search + visualisations
│   ├── search.html                ← Search & filter results
│   ├── taxonomy.html              ← Full taxonomy browser (collapsible)
│   ├── paper.html                 ← Individual paper detail
│   └── 404.html
│
├── static/                        ← Pipeline output images served by Flask
│   ├── apt_taxonomy_tree.png
│   ├── apt_dendrogram.png
│   ├── silhouette_scores.png
│   └── corpus_distribution.png
│
├── apt_papers_raw.csv             ← 120 scraped papers
├── apt_papers_clean.csv           ← Cleaned corpus
└── final_taxonomy_mapping.csv     ← Taxonomy output (main result)
```

---

## Methodology Summary

| Stage | Component | Method |
|-------|-----------|--------|
| Data collection | Semantic Scholar API | 5 APT query strings × 6 years; dual-group relevance filter (Group A: APT signals, Group B: TTP signals) |
| NLP preprocessing | NLTK | 8-step pipeline: HTML decode → URL removal → ASCII normalisation → lowercase → stop-word removal → min-length filter → lemmatisation |
| Embedding | sentence-transformers | `all-mpnet-base-v2`, 768-dim, L2-normalised so Euclidean ≡ cosine |
| Clustering | scipy HAC | Ward linkage, Euclidean distance; k=7 validated by silhouette sweep |
| Labeling | Custom | Semantic Centroid Matching: cluster centroid vs. 12 gold labels → cosine similarity matrix → Hungarian algorithm |
| Sub-clustering | scipy HAC | Depth-2: each main cluster split into k=2 sub-clusters using same method |

---

## Citation

```bibtex
@misc{apt_taxonomy_2025,
  title   = {APT Taxonomy Intelligence: An Automated ML Pipeline for
             Hierarchical Classification of APT Research Literature},
  author  = {Kanik Kumar},
  year    = {2025},
  school  = {BITS Pilani, Pilani Campus},
  note    = {CS F266 Study Project. Supervisor: Prof. Rajesh Kumar.
             GitHub: https://github.com/Kanik0575/apt-taxonomy-intelligence}
}
```

---

*Built with: Python · Flask · sentence-transformers · scipy · NLTK · scikit-learn · networkx · matplotlib · Tailwind CSS*

*Kanik Kumar · Computer Science · BITS Pilani, Pilani Campus · 2025–2026*
