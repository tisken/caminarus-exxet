#!/usr/bin/env python3
"""Re-extrae Prometheum Exxet respetando columnas (izq->der, arriba->abajo)."""
from __future__ import annotations

import re
from pathlib import Path

import pymupdf

PDF_PATH = Path("/animu/data/docs/Anima Beyond Fantasy - Prometheum exxet.pdf")
OUTPUT_PATH = Path("/animu/data/docs_md/Anima Beyond Fantasy - Prometheum exxet_columns.md")

# Pages with artifact compendium (chapter 3 onwards, roughly page 35+)
COMPENDIUM_START = 34  # 0-indexed, PDF page 35


def extract_page_columns(page):
    """Extract text blocks sorted by column (left then right), top to bottom."""
    blocks = page.get_text("blocks")
    mid_x = page.rect.width / 2

    left = sorted([b for b in blocks if b[0] < mid_x and b[4].strip()], key=lambda b: b[1])
    right = sorted([b for b in blocks if b[0] >= mid_x and b[4].strip()], key=lambda b: b[1])

    lines = []
    for b in left:
        text = b[4].strip()
        # Skip page numbers and watermarks
        if re.match(r"^\d+$", text):
            continue
        if "order #" in text.lower():
            continue
        if "Francisco Jose" in text:
            continue
        lines.append(text)

    for b in right:
        text = b[4].strip()
        if re.match(r"^\d+$", text):
            continue
        if "order #" in text.lower():
            continue
        if "Francisco Jose" in text:
            continue
        if "Ilustrado por" in text:
            continue
        lines.append(text)

    return "\n\n".join(lines)


def main():
    doc = pymupdf.open(str(PDF_PATH))
    print(f"PDF: {len(doc)} pages")

    output_lines = [
        "# Prometheum Exxet (extracción por columnas)\n",
        f"Páginas extraídas: {COMPENDIUM_START + 1} a {len(doc)}\n",
    ]

    for i in range(COMPENDIUM_START, len(doc)):
        page = doc[i]
        text = extract_page_columns(page)
        if text.strip():
            output_lines.append(f"\n---\n_Página {i + 1}_\n")
            output_lines.append(text)

    doc.close()

    output = "\n".join(output_lines)
    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(f"Output: {OUTPUT_PATH} ({len(output)} chars)")

    # Quick stats
    weapon_tables = len(re.findall(r"Daño\s+Turno\s+FUE", output, re.IGNORECASE))
    armor_tables = len(re.findall(r"Requ.*?Armadura.*?Pen.*?Natural", output, re.IGNORECASE))
    nivel_poder = len(re.findall(r"Nivel de Poder:", output, re.IGNORECASE))
    print(f"Weapon tables: {weapon_tables}, Armor tables: {armor_tables}, Nivel de Poder: {nivel_poder}")


if __name__ == "__main__":
    main()
