# Lockstep — Business Plan

**Lockstep** (working title) is the certainty platform for UK residential sales: sale-ready pack on the listing, binding reservation at offer, partners to completion — **fees on the table**, sold through agents.

Planning docs only. Open **`report/index.html`** for the presentable deck (toggle light in the nav).

---

## Contents

| Document | Description |
|----------|-------------|
| [docs/00-executive-summary.md](docs/00-executive-summary.md) | One-page synthesis |
| [docs/01-market-and-problem.md](docs/01-market-and-problem.md) | Market size, statistics, problem clusters, Scotland proof point |
| [docs/02-product-and-mechanics.md](docs/02-product-and-mechanics.md) | Product, two-layer model, flows, chain handling |
| [docs/03-economics.md](docs/03-economics.md) | Revenue model and unit economics (illustrative) |
| [docs/04-competition-and-risk.md](docs/04-competition-and-risk.md) | Competitors, precedents, risk register, mitigations |
| [docs/05-go-to-market.md](docs/05-go-to-market.md) | Agent adoption, product surfaces, roadmap, metrics |
| [docs/06-sources-and-glossary.md](docs/06-sources-and-glossary.md) | Source index and plain-English glossary |
| [financials/unit-economics.csv](financials/unit-economics.csv) | Editable model inputs |
| [report/index.html](report/index.html) | Generated presentable report |

---

## Rebuild the report

```bash
cd plan
pip install -r scripts/requirements.txt
python scripts/generate_charts.py
python scripts/build_report.py
```

Output:

- `charts/*.png` — sourced market charts + illustrative financial charts
- `report/index.html` — single styled HTML report with embedded charts and Mermaid diagrams

---

## Conventions

- **Market statistics** — sourced from published reports; see [docs/06-sources-and-glossary.md](docs/06-sources-and-glossary.md).
- **Financial model** — illustrative assumptions for planning; labelled as such in [docs/03-economics.md](docs/03-economics.md).
- **Positioning** — transparent middleman: disclosed referral/partner fees; openness as brand differentiator.
- **Acronyms** — expanded on first use in each doc; full glossary in doc 06.

---

*Last updated: June 2026*
