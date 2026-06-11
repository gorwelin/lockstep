#!/usr/bin/env python3
"""Generate sourced market charts and illustrative financial charts for Lockstep docs."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brand_palette import get_palette

ROOT = Path(__file__).resolve().parent.parent
CHARTS_DIR = ROOT / "charts"
FINANCIALS = ROOT / "financials" / "unit-economics.csv"

plt.style.use("seaborn-v0_8-darkgrid")
_chart = get_palette()["chart"]
COLORS = {
    "primary": _chart["primary"],
    "secondary": _chart["secondary"],
    "accent": _chart["accent"],
    "muted": "#8fa3be",
    "positive": _chart["positive"],
    "negative": _chart["negative"],
    "bg": "#141c28",
    "text": "#e8eef6",
    "grid": "#243044",
}


def _style_axes(ax: plt.Axes) -> None:
    ax.set_facecolor(COLORS["bg"])
    ax.figure.set_facecolor(COLORS["bg"])
    ax.tick_params(colors=COLORS["text"])
    ax.xaxis.label.set_color(COLORS["text"])
    ax.yaxis.label.set_color(COLORS["text"])
    ax.title.set_color(COLORS["text"])
    for spine in ax.spines.values():
        spine.set_color(COLORS["grid"])
    ax.grid(True, color=COLORS["grid"], alpha=0.6)


def save(fig: plt.Figure, name: str) -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    path = CHARTS_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=COLORS["bg"])
    plt.close(fig)
    print(f"  wrote {path.relative_to(ROOT)}")


def chart_fallthrough_trend() -> None:
    years = ["2022", "2024"]
    rates = [16, 29.8]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(years, rates, color=[COLORS["secondary"], COLORS["accent"]], width=0.5)
    ax.set_ylabel("Fall-through rate (%)")
    ax.set_title("UK property transaction fall-through rate", fontweight="bold")
    ax.set_ylim(0, 35)
    for bar, val in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8, f"{val}%", ha="center", fontweight="bold")
    ax.text(0.5, -0.18, "Source: GOTO Group 2024 (The Negotiator / AIM Group)", transform=ax.transAxes, ha="center", fontsize=9, color=COLORS["muted"])
    _style_axes(ax)
    save(fig, "01-fallthrough-trend.png")


def chart_england_scotland() -> None:
    regions = ["Scotland\n(ESPC 2023)", "England\n(Quick Move Now 2023)"]
    rates = [8.7, 27.3]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(regions, rates, color=[COLORS["positive"], COLORS["negative"]], width=0.55)
    ax.set_ylabel("Fall-through rate (%)")
    ax.set_title("Fall-through: Scotland vs England", fontweight="bold")
    ax.set_ylim(0, 35)
    for bar, val in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.6, f"{val}%", ha="center", fontweight="bold")
    ax.text(0.5, -0.15, "Source: ESPC (Jul–Oct 2023 Scotland; Jul–Sep 2023 England)", transform=ax.transAxes, ha="center", fontsize=9, color=COLORS["muted"])
    _style_axes(ax)
    save(fig, "02-england-vs-scotland-fallthrough.png")


def chart_fallthrough_causes() -> None:
    causes = ["Bad survey\n(GOTO)", "Mortgage\n(GOTO)", "Chain\n(Barclays)", "Gazumping\n(Barclays)", "Gazundering\n(Barclays)"]
    values = [27.3, 22, 22, 13, 11]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(causes, values, color=COLORS["primary"])
    ax.set_xlabel("Share of fall-throughs (%)")
    ax.set_title("Primary causes of property fall-through", fontweight="bold")
    ax.invert_yaxis()
    for bar, val in zip(bars, values):
        ax.text(val + 0.5, bar.get_y() + bar.get_height() / 2, f"{val}%", va="center")
    ax.text(0.5, -0.12, "Sources: GOTO 2024; Barclays survey via Estate Agent Today 2026", transform=ax.transAxes, ha="center", fontsize=9, color=COLORS["muted"])
    _style_axes(ax)
    save(fig, "03-fallthrough-causes.png")


def chart_transaction_time() -> None:
    years = ["2014", "2024"]
    days = [94, 122]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(years, days, color=[COLORS["secondary"], COLORS["accent"]], width=0.5)
    ax.set_ylabel("Days (offer to completion)")
    ax.set_title("Average time to buy a UK property (+30%)", fontweight="bold")
    for bar, val in zip(bars, days):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2, f"{val} days", ha="center", fontweight="bold")
    ax.text(0.5, -0.15, "Source: TwentyCi via HomeOwners Alliance 2025", transform=ax.transAxes, ha="center", fontsize=9, color=COLORS["muted"])
    _style_axes(ax)
    save(fig, "04-transaction-time-trend.png")


def chart_leasehold_concern() -> None:
    labels = ["2015", "2025"]
    values = [42, 64]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=[COLORS["muted"], COLORS["accent"]], width=0.45)
    ax.set_ylabel("% rating leasehold a serious concern")
    ax.set_title("Rising concern: UK leasehold system (+22pp)", fontweight="bold")
    ax.set_ylim(0, 80)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5, f"{val}%", ha="center", fontweight="bold")
    ax.text(0.5, -0.15, "Source: HomeOwners Alliance HomeOwners Survey 2025", transform=ax.transAxes, ha="center", fontsize=9, color=COLORS["muted"])
    _style_axes(ax)
    save(fig, "05-housing-concerns-leasehold.png")


def load_economics() -> dict[str, dict[str, float]]:
    rows: dict[str, dict[str, float]] = {}
    with FINANCIALS.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows[row["line"]] = {
                "full": float(row["full_value_gbp"]),
                "attach_c": float(row["attach_rate_conservative"]),
                "attach_b": float(row["attach_rate_base"]),
                "attach_o": float(row["attach_rate_optimistic"]),
                "cost": float(row["cost_per_deal_gbp"]),
            }
    return rows


def weighted_revenue(rows: dict, attach_key: str) -> tuple[list[str], list[float]]:
    labels = []
    values = []
    mapping = [
        ("reservation_fee", "Reservation fee"),
        ("conveyancing_referral_buyer", "Conveyancing (buyer)"),
        ("conveyancing_referral_seller", "Conveyancing (seller)"),
        ("mortgage_referral", "Mortgage referral"),
        ("survey_referral", "Survey referral"),
        ("insurance_commission", "Insurance"),
    ]
    for key, label in mapping:
        r = rows[key]
        val = r["full"] * r[attach_key]
        if val > 0:
            labels.append(label)
            values.append(val)
    return labels, values


def chart_revenue_stack() -> None:
    rows = load_economics()
    labels, values = weighted_revenue(rows, "attach_b")
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, values, color=COLORS["primary"])
    ax.set_ylabel("Weighted revenue (£)")
    ax.set_title("Revenue stack per completed deal — base case (illustrative)", fontweight="bold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:,.0f}"))
    plt.xticks(rotation=25, ha="right")
    total = sum(values)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 8, f"£{val:.0f}", ha="center", fontsize=9)
    ax.text(0.5, -0.22, f"Total gross: £{total:.0f} | Illustrative model — see docs/03-economics.md", transform=ax.transAxes, ha="center", fontsize=9, color=COLORS["muted"])
    _style_axes(ax)
    save(fig, "06-revenue-stack-base.png")


def chart_competitor_scale() -> None:
    labels = ["Gazeal\nnet assets (£k)", "Moverly\nfunding ($M)", "Upstix\npre-tax loss (£M)"]
    values = [-243, 1.22, 7.25]
    colors = [COLORS["negative"], COLORS["secondary"], COLORS["negative"]]
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(labels, values, color=colors, width=0.55)
    ax.axhline(0, color=COLORS["muted"], linewidth=0.8)
    ax.set_title("Competitor / precedent scale snapshot", fontweight="bold")
    ax.set_ylabel("Value (mixed units — see labels)")
    for bar, val in zip(bars, values):
        y = val + (0.15 if val >= 0 else -0.35)
        ax.text(bar.get_x() + bar.get_width() / 2, y, f"{val}", ha="center", fontweight="bold")
    ax.text(0.5, -0.15, "Sources: Endole (Gazeal); Company Check (Moverly); Pomanda (Upstix)", transform=ax.transAxes, ha="center", fontsize=9, color=COLORS["muted"])
    _style_axes(ax)
    save(fig, "08-competitor-scale.png")


def main() -> None:
    print("Generating Lockstep charts...")
    chart_fallthrough_trend()
    chart_england_scotland()
    chart_fallthrough_causes()
    chart_transaction_time()
    chart_leasehold_concern()
    chart_revenue_stack()
    chart_competitor_scale()
    print("Done.")


if __name__ == "__main__":
    main()
