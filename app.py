"""
APT Taxonomy Intelligence Explorer — Flask Web Application
==========================================================
Interactive search and browse interface over the APT research taxonomy.

Routes
------
  GET /                    Home: taxonomy overview + search entry
  GET /search              Search/filter papers (q, year, cluster)
  GET /paper/<paper_id>    Paper detail page
  GET /taxonomy            Full taxonomy tree view
  GET /api/papers          JSON API endpoint

Run locally
-----------
  pip install flask
  python app.py
  Open http://localhost:5000
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# ── Data loading ──────────────────────────────────────────────────────────────

DATA_DIR = Path(__file__).parent

def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load taxonomy mapping and clean papers CSVs. Merge for full detail."""
    taxonomy = pd.read_csv(DATA_DIR / "final_taxonomy_mapping.csv", encoding="utf-8")
    clean = pd.read_csv(DATA_DIR / "apt_papers_clean.csv", encoding="utf-8")

    # Merge to bring in abstract and URL
    merged = taxonomy.merge(
        clean[["paper_id", "abstract", "url", "venue"]],
        on="paper_id",
        how="left",
        suffixes=("", "_clean"),
    )
    # Prefer venue from taxonomy if present, else clean
    if "venue_clean" in merged.columns:
        merged["venue"] = merged["venue"].fillna(merged["venue_clean"])
        merged = merged.drop(columns=["venue_clean"])

    return merged, taxonomy


df_papers, df_taxonomy = load_data()


# ── Taxonomy structure ────────────────────────────────────────────────────────

CLUSTER_COLORS = {
    1: "#e6194b",
    2: "#3cb44b",
    3: "#4363d8",
    4: "#f58231",
    5: "#911eb4",
    6: "#42d4f4",
    7: "#f032e6",
}

CLUSTER_PASTEL = {
    1: "#fecaca",
    2: "#bbf7d0",
    3: "#bfdbfe",
    4: "#fed7aa",
    5: "#e9d5ff",
    6: "#a5f3fc",
    7: "#f9a8d4",
}


def build_taxonomy_tree() -> list[dict]:
    """Build a JSON-serialisable taxonomy tree from the mapping CSV."""
    tree = []
    for cid in sorted(df_taxonomy["cluster_id"].unique()):
        cluster_rows = df_taxonomy[df_taxonomy["cluster_id"] == cid]
        cluster_label = cluster_rows["cluster_label"].iloc[0]

        sub_nodes = []
        for sid in sorted(cluster_rows["sub_id"].unique()):
            sub_rows = cluster_rows[cluster_rows["sub_id"] == sid]
            sub_label = sub_rows["sub_label"].iloc[0]
            sub_nodes.append({
                "sub_id": int(sid),
                "label": sub_label,
                "count": len(sub_rows),
            })

        tree.append({
            "cluster_id": int(cid),
            "label": cluster_label,
            "count": len(cluster_rows),
            "color": CLUSTER_COLORS.get(cid, "#888888"),
            "pastel": CLUSTER_PASTEL.get(cid, "#e2e8f0"),
            "sub_clusters": sub_nodes,
        })
    return tree


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Home page: summary stats + taxonomy overview + search entry."""
    tree = build_taxonomy_tree()
    stats = {
        "total_papers": len(df_papers),
        "years": sorted(df_papers["year"].dropna().unique().astype(int).tolist()),
        "clusters": len(df_papers["cluster_id"].unique()),
        "year_range": f"{int(df_papers['year'].min())}–{int(df_papers['year'].max())}",
    }
    recent = (
        df_papers.sort_values("year", ascending=False)
        .head(6)[["paper_id", "title", "year", "authors", "cluster_label", "cluster_id"]]
        .to_dict(orient="records")
    )
    return render_template("index.html", tree=tree, stats=stats, recent=recent,
                           cluster_colors=CLUSTER_COLORS, cluster_pastel=CLUSTER_PASTEL)


@app.route("/search")
def search():
    """Search and filter papers."""
    q = request.args.get("q", "").strip().lower()
    year = request.args.get("year", "").strip()
    cluster = request.args.get("cluster", "").strip()

    results = df_papers.copy()

    if q:
        mask = (
            results["title"].str.lower().str.contains(q, na=False) |
            results["authors"].str.lower().str.contains(q, na=False) |
            results["abstract"].str.lower().str.contains(q, na=False) |
            results["cluster_label"].str.lower().str.contains(q, na=False)
        )
        results = results[mask]

    if year:
        try:
            results = results[results["year"] == int(year)]
        except ValueError:
            pass

    if cluster:
        try:
            results = results[results["cluster_id"] == int(cluster)]
        except ValueError:
            pass

    records = (
        results[["paper_id", "title", "year", "authors", "venue",
                  "cluster_id", "cluster_label", "sub_id", "sub_label", "url"]]
        .fillna("")
        .head(100)
        .to_dict(orient="records")
    )

    years = sorted(df_papers["year"].dropna().unique().astype(int).tolist())
    clusters = (
        df_papers[["cluster_id", "cluster_label"]]
        .drop_duplicates()
        .sort_values("cluster_id")
        .to_dict(orient="records")
    )

    return render_template(
        "search.html",
        results=records,
        q=request.args.get("q", ""),
        year=year,
        cluster=cluster,
        total=len(results),
        years=years,
        clusters=clusters,
        cluster_colors=CLUSTER_COLORS,
        cluster_pastel=CLUSTER_PASTEL,
    )


@app.route("/paper/<paper_id>")
def paper_detail(paper_id: str):
    """Individual paper detail page."""
    row = df_papers[df_papers["paper_id"] == paper_id]
    if row.empty:
        return render_template("404.html"), 404

    paper = row.iloc[0].to_dict()

    # Sibling papers in same cluster
    siblings = (
        df_papers[
            (df_papers["cluster_id"] == paper["cluster_id"]) &
            (df_papers["paper_id"] != paper_id)
        ]
        .sort_values("year", ascending=False)
        .head(5)[["paper_id", "title", "year", "authors", "cluster_label"]]
        .to_dict(orient="records")
    )

    return render_template(
        "paper.html",
        paper=paper,
        siblings=siblings,
        color=CLUSTER_COLORS.get(paper["cluster_id"], "#888"),
        pastel=CLUSTER_PASTEL.get(paper["cluster_id"], "#eee"),
    )


@app.route("/taxonomy")
def taxonomy():
    """Full taxonomy tree view with all papers."""
    tree = build_taxonomy_tree()
    papers_by_cluster = {}
    for cid in df_papers["cluster_id"].unique():
        papers_by_cluster[int(cid)] = (
            df_papers[df_papers["cluster_id"] == cid]
            .sort_values("year", ascending=False)
            [["paper_id", "title", "year", "authors", "sub_label", "sub_id", "url"]]
            .to_dict(orient="records")
        )

    return render_template(
        "taxonomy.html",
        tree=tree,
        papers_by_cluster=papers_by_cluster,
        cluster_colors=CLUSTER_COLORS,
        cluster_pastel=CLUSTER_PASTEL,
    )


@app.route("/api/papers")
def api_papers():
    """JSON API: search papers."""
    q = request.args.get("q", "").strip().lower()
    year = request.args.get("year", "")
    cluster = request.args.get("cluster", "")
    limit = min(int(request.args.get("limit", 50)), 200)

    results = df_papers.copy()
    if q:
        mask = (
            results["title"].str.lower().str.contains(q, na=False) |
            results["cluster_label"].str.lower().str.contains(q, na=False)
        )
        results = results[mask]
    if year:
        results = results[results["year"] == int(year)]
    if cluster:
        results = results[results["cluster_id"] == int(cluster)]

    out = (
        results[["paper_id", "title", "year", "authors", "venue",
                  "cluster_id", "cluster_label", "sub_id", "sub_label", "url"]]
        .fillna("")
        .head(limit)
        .to_dict(orient="records")
    )
    return jsonify({"total": len(results), "papers": out})


@app.route("/api/taxonomy")
def api_taxonomy():
    """JSON API: full taxonomy tree."""
    return jsonify(build_taxonomy_tree())


if __name__ == "__main__":
    app.run(debug=True, port=8080)
