# Product Thinking: APT Taxonomy Intelligence as an Analyst Tool

> **Context:** This document explores what it would look like to evolve this research pipeline into a product for threat intelligence professionals. Written as part of a CS F266 Study Project at BITS Pilani.

---

## The Problem

Threat intelligence analysts spend a disproportionate share of their time on a task that should be automated: **finding relevant prior research**.

When an analyst encounters an APT campaign — say, a lateral movement pattern matching APT29's toolchain — they need to answer several questions fast:
- What does the academic literature say about this TTP?
- Which detection approaches have been validated against this class of attack?
- What forensic methods have been applied to similar intrusion sets?

Today, that means Googling, skimming CVE databases, checking vendor blogs, and manually sifting through Google Scholar. It is slow, inconsistent, and not reproducible across an organisation.

---

## The Core Use Case

**"I've identified a technique. Show me everything the research community knows about it, organised by what's actually useful to me right now."**

The taxonomy built by this pipeline is a structured, ML-derived map of how the research community thinks about APT attacks. That map is the core product asset.

---

## Target Users

| Persona | Role | Primary Pain |
|---------|------|-------------|
| **SOC Analyst (L2/L3)** | Investigates active incidents | No time to read papers; needs summaries and detection rules |
| **Threat Intelligence Researcher** | Profiles APT groups | Needs comprehensive, citable literature coverage |
| **Security Engineer** | Builds detection logic | Wants empirically-validated detection methods |
| **CISO / Security Lead** | Prioritises defensive investment | Needs to understand threat landscape at category level |

The **beachhead user** is the Threat Intelligence Researcher — they already read papers, so the taxonomy gives them immediate value with minimal behaviour change.

---

## Onboarding Flow

A new analyst lands on the tool. Here is what the ideal first 5 minutes looks like:

```
1. ENTRY  — Search a known technique or group name
             (e.g., "lateral movement", "APT29", "provenance graph")

2. ORIENT — See the taxonomy cluster this technique lives in,
             with a count of how many papers cover it
             → "Lateral Movement & C2 Infrastructure: 18 papers"

3. DRILL  — Open the cluster. See papers ranked by recency.
             Each card shows: title, venue, year, sub-category

4. READ   — Click a paper. Abstract + direct link to full text.
             See related papers in the same sub-cluster.

5. EXPORT — Download the cluster as a JSON/CSV for further analysis
             or to cite in an internal threat report
```

**Time to first value: under 60 seconds.**

No account required for the first session. The taxonomy is pre-built; there is nothing to configure.

---

## What Makes This Different From Google Scholar

| | Google Scholar | This Tool |
|---|---|---|
| **Structure** | Flat keyword results | Hierarchical taxonomy (ML-derived) |
| **Domain filter** | General academic | APT-specific (dual-group relevance filter) |
| **Cluster context** | None | Shows which research community a paper belongs to |
| **Related papers** | Citation graph only | Semantic similarity within taxonomy cluster |
| **Coverage** | Everything | Curated: only papers with both APT-level AND TTP-level signal |

---

## Feature Prioritisation (MoSCoW)

### Must Have (MVP — live now)
- [x] Full-text search across 120 papers
- [x] Filter by year, cluster, sub-cluster
- [x] Individual paper detail pages with abstract
- [x] Direct links to open-access PDFs
- [x] JSON API for programmatic access

### Should Have (v1.1)
- [ ] Keyword-level search highlighting in abstracts
- [ ] "Similar papers" beyond same cluster (cosine distance ranking)
- [ ] Downloadable cluster reports (PDF / CSV)
- [ ] Semantic Scholar citation count surfaced per paper

### Could Have (v2)
- [ ] Natural language query interface ("show me papers about detecting lateral movement using graphs")
- [ ] Alert: "3 new papers published this month in your saved clusters"
- [ ] MITRE ATT&CK tactic mapping overlaid on taxonomy clusters
- [ ] User-defined saved searches

### Won't Have (this scope)
- User accounts / auth (adds friction, no value for a research tool)
- Proprietary threat feeds (out of scope, licensing complexity)
- Real-time scraping (pipeline is designed for reproducible batch runs)

---

## Metrics That Define Success

### North Star Metric
**Papers accessed per analyst per week** — a proxy for whether the taxonomy is actually surfacing useful research, not just existing.

### Supporting Metrics

| Metric | Why It Matters | Target (90 days) |
|--------|---------------|-----------------|
| Search-to-paper click rate | Validates taxonomy labels are meaningful | > 40% |
| Cluster browse depth | Measures taxonomy utility beyond search | > 2 clusters/session |
| Return visit rate (7-day) | Indicates habit formation | > 25% |
| API call volume | Signals integration into analyst workflows | > 100 calls/week |

### Anti-Metrics (watch for degradation)
- Time-to-first-paper > 30 seconds → search is broken or taxonomy is opaque
- Bounce rate on cluster pages > 70% → labels are not matching analyst mental models

---

## The Core Design Principle

**The taxonomy is a navigation layer, not a knowledge layer.**

This tool does not summarise papers or generate insights — those are hard AI problems with hallucination risk. Instead, it does something simpler and more trustworthy: it organises existing, peer-reviewed research into a structure that mirrors how security practitioners already think about APT attacks.

That constraint is a feature. An analyst can trust a result because they can click through to the original paper. The ML model is used for *organisation*, not *generation*.

---

## Honest Limitations

1. **120 papers is a small corpus.** Cluster boundaries shift meaningfully when 20 new papers are added. The pipeline needs to be re-run periodically (quarterly is reasonable).

2. **`all-mpnet-base-v2` is not cybersecurity-specific.** A domain-fine-tuned model (SecBERT, CySecBERT) would produce tighter clusters. This is a known trade-off documented in the codebase.

3. **Label quality depends on gold-standard labels.** The Hungarian algorithm assigns the best fit from a predefined list. If the corpus shifts toward a new attack class not covered by the gold labels, a cluster will receive a semantically distant label.

4. **No temporal freshness signal.** A 2021 paper and a 2026 paper are treated as equally relevant unless the analyst filters by year.

---

## If This Were a Product: The Pitch

> *"Threat intelligence analysts waste hours every week manually searching for relevant APT research. APT Taxonomy Intelligence is a structured, ML-organised research navigator that cuts that search to under a minute — giving analysts a citable, cluster-mapped view of 120 peer-reviewed papers, searchable by technique, threat actor, year, or detection method."*

**Buyer:** Security Operations teams, threat intelligence platforms (Recorded Future, ThreatConnect integration)  
**Distribution:** Self-serve; embed in existing SIEM/TIP workflows via JSON API  
**Monetisation:** Freemium — free public taxonomy, paid API access with freshness SLAs and custom corpora

---

*Kanik Kumar · BITS Pilani · CS F266 Study Project · 2025–2026*
