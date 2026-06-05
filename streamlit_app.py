"""
APT Research Navigator — Streamlit Web Application
====================================================
Interactive taxonomy browser and search interface over 120 APT security papers.
Deployed at: https://share.streamlit.io

Run locally:  streamlit run streamlit_app.py
"""

import pandas as pd
import streamlit as st
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="APT Research Navigator",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Hide Streamlit branding */
  #MainMenu, footer { visibility: hidden; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

  /* Metric cards */
  [data-testid="metric-container"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }

  /* Cluster badge */
  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    color: white;
    margin-right: 4px;
  }

  /* Paper card */
  .paper-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    border-left: 4px solid #4363d8;
  }

  /* Section headers */
  .section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.5rem;
    padding-bottom: 6px;
    border-bottom: 2px solid #f1f5f9;
  }

  .stTabs [data-baseweb="tab-list"] { gap: 8px; }
  .stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    font-weight: 600;
  }
  div[data-testid="stExpander"] details summary p { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Data loading ──────────────────────────────────────────────────────────────
BASE = Path(__file__).parent

CLUSTER_COLORS = {
    1: "#e6194b", 2: "#3cb44b", 3: "#4363d8",
    4: "#f58231", 5: "#911eb4", 6: "#42d4f4", 7: "#f032e6",
}
CLUSTER_PASTEL = {
    1: "#fecaca", 2: "#bbf7d0", 3: "#bfdbfe",
    4: "#fed7aa", 5: "#e9d5ff", 6: "#a5f3fc", 7: "#f9a8d4",
}

@st.cache_data
def load_data():
    taxonomy = pd.read_csv(BASE / "final_taxonomy_mapping.csv")
    clean    = pd.read_csv(BASE / "apt_papers_clean.csv")
    df = taxonomy.merge(
        clean[["paper_id", "abstract", "url"]],
        on="paper_id", how="left"
    )
    df["url"]      = df["url"].fillna("")
    df["abstract"] = df["abstract"].fillna("")
    df["authors"]  = df["authors"].fillna("Unknown")
    df["venue"]    = df["venue"].fillna("")
    df["year"]     = df["year"].astype(int)
    return df

df = load_data()

def cluster_label(cid: int) -> str:
    row = df[df["cluster_id"] == cid]["cluster_label"].iloc[0]
    return row

def badge_html(cid: int, text: str) -> str:
    color = CLUSTER_COLORS.get(cid, "#888")
    return f'<span class="badge" style="background:{color}">{text}</span>'

# ── Header ────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("""
    <h1 style='font-size:2rem; font-weight:800; color:#0f172a; margin-bottom:0'>
      🔐 APT Research Navigator
    </h1>
    <p style='color:#64748b; font-size:1rem; margin-top:4px'>
      120 peer-reviewed APT security papers (2021–2026) · Ward Hierarchical Clustering ·
      Semantic Centroid Matching · BITS Pilani CS F266
    </p>
    """, unsafe_allow_html=True)
with col_h2:
    st.markdown("""
    <div style='text-align:right; padding-top:8px'>
      <a href="https://github.com/Kanik0575/apt-research-navigator" target="_blank"
         style='background:#1e293b; color:white; padding:8px 16px; border-radius:8px;
                text-decoration:none; font-weight:600; font-size:0.85rem'>
        ⭐ GitHub
      </a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠  Overview",
    "🔍  Search Papers",
    "🗂️  Taxonomy Browser",
    "⚙️  Pipeline & Methods",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Papers Analysed", len(df), help="Real papers from Semantic Scholar API")
    m2.metric("Taxonomy Clusters", df["cluster_id"].nunique(), help="Top-level HAC clusters at k=7")
    m3.metric("Embedding Dims", "768", help="all-mpnet-base-v2 sentence transformer")
    m4.metric("Year Coverage", f"{df['year'].min()}–{df['year'].max()}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Cluster overview
    st.markdown("<div class='section-header'>Taxonomy Structure</div>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, cid in enumerate(sorted(df["cluster_id"].unique())):
        sub = df[df["cluster_id"] == cid]
        label = sub["cluster_label"].iloc[0]
        count = len(sub)
        color = CLUSTER_COLORS.get(cid, "#888")
        pastel = CLUSTER_PASTEL.get(cid, "#eee")
        sub_labels = sub.groupby("sub_label").size().reset_index()
        sub_text = " · ".join(
            f"{r['sub_label']} ({r[0]})" for _, r in sub_labels.iterrows()
        )
        with cols[i % 2]:
            st.markdown(f"""
            <div style='background:{pastel}20; border:1px solid {pastel};
                        border-left:4px solid {color}; border-radius:10px;
                        padding:12px 16px; margin-bottom:10px'>
              <div style='font-weight:700; color:#1e293b'>
                <span style='background:{color}; color:white; padding:2px 8px;
                             border-radius:4px; font-size:11px; margin-right:8px'>C{cid}</span>
                {label}
                <span style='float:right; background:{color}; color:white;
                             padding:2px 8px; border-radius:6px; font-size:12px'>{count}</span>
              </div>
              <div style='font-size:11px; color:#64748b; margin-top:6px'>{sub_text}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Visualisations
    st.markdown("<div class='section-header'>ML Output Visualisations</div>", unsafe_allow_html=True)
    v1, v2 = st.columns(2)
    tree_img = BASE / "static" / "apt_taxonomy_tree.png"
    dend_img = BASE / "static" / "apt_dendrogram.png"
    sil_img  = BASE / "static" / "silhouette_scores.png"
    corp_img = BASE / "static" / "corpus_distribution.png"
    if tree_img.exists():
        with v1:
            st.image(str(tree_img), caption="Taxonomy Hierarchy Tree — Root → 7 clusters → 14 sub-clusters", use_container_width=True)
    if dend_img.exists():
        with v2:
            st.image(str(dend_img), caption="Ward Agglomerative Clustering Dendrogram (k=7 cut shown)", use_container_width=True)

    s1, s2 = st.columns(2)
    if sil_img.exists():
        with s1:
            st.image(str(sil_img), caption="Silhouette Score Sweep — validates k=7 as optimal cluster count", use_container_width=True)
    if corp_img.exists():
        with s2:
            st.image(str(corp_img), caption="Corpus Distribution by Publication Year (2021–2026)", use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SEARCH
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    s_col1, s_col2, s_col3 = st.columns([3, 1, 2])
    with s_col1:
        query = st.text_input("Search papers", placeholder="e.g.  lateral movement,  APT29,  provenance graph", label_visibility="collapsed")
    with s_col2:
        year_opts = ["All years"] + sorted(df["year"].unique().tolist(), reverse=True)
        sel_year = st.selectbox("Year", year_opts, label_visibility="collapsed")
    with s_col3:
        cluster_opts = {"All clusters": 0}
        for cid in sorted(df["cluster_id"].unique()):
            cluster_opts[f"C{cid}: {cluster_label(cid)}"] = cid
        sel_cluster_label = st.selectbox("Cluster", list(cluster_opts.keys()), label_visibility="collapsed")
        sel_cluster = cluster_opts[sel_cluster_label]

    # Filter
    results = df.copy()
    if query:
        q = query.lower()
        mask = (
            results["title"].str.lower().str.contains(q, na=False) |
            results["authors"].str.lower().str.contains(q, na=False) |
            results["abstract"].str.lower().str.contains(q, na=False) |
            results["cluster_label"].str.lower().str.contains(q, na=False)
        )
        results = results[mask]
    if sel_year != "All years":
        results = results[results["year"] == int(sel_year)]
    if sel_cluster:
        results = results[results["cluster_id"] == sel_cluster]

    st.caption(f"**{len(results)}** papers" + (f' matching "{query}"' if query else ""))

    if results.empty:
        st.info("No papers found. Try a different keyword.")
    else:
        for _, p in results.head(50).iterrows():
            cid   = int(p["cluster_id"])
            color = CLUSTER_COLORS.get(cid, "#888")
            pastel = CLUSTER_PASTEL.get(cid, "#eee")
            with st.expander(f"**{p['title']}**  ·  {int(p['year'])}"):
                a_col, b_col = st.columns([3, 1])
                with a_col:
                    st.markdown(f"**Authors:** {p['authors']}")
                    if p["venue"]:
                        st.markdown(f"**Venue:** *{p['venue']}*")
                    st.markdown(f"""
                    {badge_html(cid, f"C{cid}: {p['cluster_label']}")}
                    <span style='background:{pastel}; color:#334155; padding:3px 10px;
                                 border-radius:20px; font-size:12px; font-weight:600'>
                      S{int(p['sub_id'])}: {p['sub_label']}
                    </span>
                    """, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(p["abstract"][:800] + ("…" if len(p["abstract"]) > 800 else ""))
                with b_col:
                    if p["url"]:
                        st.link_button("Open Paper ↗", p["url"])
                    st.caption(f"ID: `{p['paper_id'][:12]}…`")

        if len(results) > 50:
            st.caption(f"Showing top 50 of {len(results)} results.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — TAXONOMY BROWSER
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    tree_img = BASE / "static" / "apt_taxonomy_tree.png"
    if tree_img.exists():
        st.image(str(tree_img), caption="APT Research Taxonomy — Ward HAC + Semantic Centroid Matching", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Browse by Cluster</div>", unsafe_allow_html=True)

    for cid in sorted(df["cluster_id"].unique()):
        cdf = df[df["cluster_id"] == cid].sort_values("year", ascending=False)
        label = cdf["cluster_label"].iloc[0]
        color = CLUSTER_COLORS.get(cid, "#888")
        pastel = CLUSTER_PASTEL.get(cid, "#eee")

        sub_summary = ", ".join(
            f"S{int(r.sub_id)}: {r.sub_label} ({len(cdf[cdf['sub_id']==r.sub_id])})"
            for r in cdf.drop_duplicates("sub_id").itertuples()
        )

        header_html = f"""
        <span style='background:{color}; color:white; padding:3px 10px;
                     border-radius:6px; font-size:13px; font-weight:700; margin-right:10px'>C{cid}</span>
        <strong>{label}</strong>
        <span style='float:right; color:#64748b; font-size:13px'>{len(cdf)} papers</span>
        """

        with st.expander(f"C{cid}  ·  {label}  ({len(cdf)} papers)"):
            st.markdown(f"<div style='color:#64748b; font-size:12px; margin-bottom:12px'>{sub_summary}</div>", unsafe_allow_html=True)

            # Sub-cluster filter
            subs = sorted(cdf["sub_id"].unique())
            sub_filter = st.radio(
                "Sub-cluster",
                options=[0] + [int(s) for s in subs],
                format_func=lambda x: "All" if x == 0 else f"S{x}: {cdf[cdf['sub_id']==x]['sub_label'].iloc[0]} ({len(cdf[cdf['sub_id']==x])})",
                horizontal=True,
                key=f"sub_filter_{cid}",
                label_visibility="collapsed",
            )

            view = cdf if sub_filter == 0 else cdf[cdf["sub_id"] == sub_filter]

            display = view[["title", "year", "authors", "venue", "url"]].copy()
            display["authors"] = display["authors"].str.split(";").str[0].str.strip()
            display = display.rename(columns={
                "title": "Title", "year": "Year",
                "authors": "First Author", "venue": "Venue", "url": "Link"
            })
            st.dataframe(
                display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Link": st.column_config.LinkColumn("Paper", display_text="Open ↗"),
                    "Year": st.column_config.NumberColumn(format="%d", width="small"),
                },
            )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PIPELINE & METHODS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    p1, p2 = st.columns(2)

    with p1:
        st.markdown("### Pipeline")
        st.markdown("""
```
Stage 1 — scraper.py
  Semantic Scholar API · 5 APT query strings
  Dual-group relevance filter (APT signals + TTP signals)
  Output: 120 papers · 2021–2026

Stage 2 — preprocess.py
  HTML decode · URL removal · Lowercase
  Stop-word removal (200+ domain-specific)
  NLTK lemmatization
  Min-token length filter (≥3 chars)

Stage 3 — taxonomy_builder.py
  Sentence-Transformer: all-mpnet-base-v2
  768-dim L2-normalised embeddings
  Ward Agglomerative HAC (Euclidean)
  Silhouette sweep → k=7 optimal
  Semantic Centroid Matching (Hungarian)
  → 7 clusters · 14 sub-clusters
```
""")

    with p2:
        st.markdown("### Key Design Decisions")
        st.markdown("""
**Why Ward HAC instead of K-Means?**
K-Means produces flat clusters — not a hierarchy. Ward HAC builds a full
dendrogram, preserving two-level taxonomic structure.

**Why Semantic Centroid Matching instead of c-TF-IDF?**
On 120 papers, c-TF-IDF yields generic labels. Centroid Matching embeds expert
gold-standard labels and uses the Hungarian algorithm to find the globally
optimal one-to-one assignment — no two clusters share a label.

**Why `all-mpnet-base-v2`?**
Domain-specific models (SecBERT) are masked-LMs requiring custom pooling with
weaker validation for sentence-level tasks. mpnet is the defensible choice for
a small academic corpus. Honestly disclosed in the codebase.

**Raw abstracts for embedding, not cleaned text.**
Sentence-transformers expect grammatical English — lemmatised token bags
destroy contextual signal.
""")

    st.markdown("---")
    st.markdown("### Methodology Summary")
    method_df = pd.DataFrame([
        ["Data Collection",  "Semantic Scholar API",   "5 queries × 6 years · dual-group APT+TTP filter"],
        ["NLP Preprocessing","NLTK",                   "8-step: decode → URLs → ASCII → lowercase → stopwords → length → lemmatize"],
        ["Embedding",        "sentence-transformers",   "all-mpnet-base-v2 · 768-dim · L2-normalised"],
        ["Clustering",       "scipy HAC",              "Ward linkage · Euclidean · k=7 (silhouette-validated)"],
        ["Labeling",         "Custom (this project)",  "Semantic Centroid Matching + Hungarian algorithm"],
        ["Sub-clustering",   "scipy HAC",              "Depth-2: k=2 within each main cluster"],
    ], columns=["Stage", "Library", "Details"])
    st.dataframe(method_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.code("""@misc{apt_taxonomy_2025,
  title  = {APT Research Navigator: Automated Hierarchical Taxonomy of APT Research},
  author = {Kanik Kumar},
  year   = {2025},
  school = {BITS Pilani, Pilani Campus},
  note   = {CS F266 Study Project. Supervisor: Prof. Rajesh Kumar}
}""", language="bibtex")

    st.caption("Built with · sentence-transformers · scipy · NLTK · scikit-learn · networkx · matplotlib · Streamlit")
