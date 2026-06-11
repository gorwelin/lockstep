"""Brand palettes for Lockstep report + charts. Set ACTIVE to preview another option."""

from __future__ import annotations

ACTIVE = "pine_chalk"

PALETTES: dict[str, dict] = {
    "ink_brass": {
        "css_dark": {
            "brand": "#c9a227",
            "brand_dim": "rgba(201, 162, 39, 0.14)",
            "accent": "#e8dcc0",
            "accent_dim": "rgba(232, 220, 192, 0.08)",
            "link": "#dcc06a",
        },
        "css_light": {
            "brand": "#9a7b1a",
            "brand_dim": "rgba(154, 123, 26, 0.12)",
            "accent": "#5c4d2e",
            "accent_dim": "rgba(92, 77, 46, 0.08)",
            "link": "#7a6215",
        },
        "chart": {
            "primary": "#c9a227",
            "secondary": "#dcc06a",
            "accent": "#a65d4e",
            "positive": "#c9a227",
            "negative": "#a65d4e",
        },
        "mermaid_dark": {
            "primaryColor": "#c9a227",
            "lineColor": "#8fa3be",
            "primaryTextColor": "#e8eef6",
        },
        "mermaid_light": {
            "primaryColor": "#9a7b1a",
            "lineColor": "#5a6b82",
            "primaryTextColor": "#1a2332",
        },
    },
    "cold_blue": {
        "css_dark": {
            "brand": "#4cc9f0",
            "brand_dim": "rgba(76, 201, 240, 0.12)",
            "accent": "#90e0ef",
            "accent_dim": "rgba(144, 224, 239, 0.08)",
            "link": "#7dd3fc",
        },
        "css_light": {
            "brand": "#0077b6",
            "brand_dim": "rgba(0, 119, 182, 0.1)",
            "accent": "#023e8a",
            "accent_dim": "rgba(2, 62, 138, 0.08)",
            "link": "#0077b6",
        },
        "chart": {
            "primary": "#4cc9f0",
            "secondary": "#90e0ef",
            "accent": "#ff6b4a",
            "positive": "#4cc9f0",
            "negative": "#ff6b4a",
        },
        "mermaid_dark": {
            "primaryColor": "#4cc9f0",
            "lineColor": "#8fa3be",
            "primaryTextColor": "#e8eef6",
        },
        "mermaid_light": {
            "primaryColor": "#0077b6",
            "lineColor": "#5a6b82",
            "primaryTextColor": "#1a2332",
        },
    },
    "pine_chalk": {
        "css_dark": {
            "brand": "#52b788",
            "brand_dim": "rgba(82, 183, 136, 0.14)",
            "accent": "#95d5b2",
            "accent_dim": "rgba(149, 213, 178, 0.08)",
            "link": "#74c69d",
        },
        "css_light": {
            "brand": "#2d6a4f",
            "brand_dim": "rgba(45, 106, 79, 0.12)",
            "accent": "#1b4332",
            "accent_dim": "rgba(27, 67, 50, 0.08)",
            "link": "#2d6a4f",
        },
        "chart": {
            "primary": "#52b788",
            "secondary": "#95d5b2",
            "accent": "#e07a3a",
            "positive": "#52b788",
            "negative": "#e07a3a",
        },
        "mermaid_dark": {
            "primaryColor": "#52b788",
            "lineColor": "#8fa3be",
            "primaryTextColor": "#e8eef6",
        },
        "mermaid_light": {
            "primaryColor": "#2d6a4f",
            "lineColor": "#5a6b82",
            "primaryTextColor": "#1a2332",
        },
    },
}


def get_palette(name: str | None = None) -> dict:
    key = name or ACTIVE
    if key not in PALETTES:
        raise KeyError(f"Unknown palette {key!r}; choose from {list(PALETTES)}")
    return PALETTES[key]


def css_brand_block() -> str:
    """CSS custom properties for brand colours only (theme neutrals stay in template)."""
    p = get_palette()
    d, light = p["css_dark"], p["css_light"]
    return f"""      --brand: {d["brand"]};
      --brand-dim: {d["brand_dim"]};
      --accent: {d["accent"]};
      --accent-dim: {d["accent_dim"]};
      --link: {d["link"]};"""


def css_brand_block_light() -> str:
    p = get_palette()
    light = p["css_light"]
    return f"""      --brand: {light["brand"]};
      --brand-dim: {light["brand_dim"]};
      --accent: {light["accent"]};
      --accent-dim: {light["accent_dim"]};
      --link: {light["link"]};"""
