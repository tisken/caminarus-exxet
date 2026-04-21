#!/usr/bin/env python3
"""Busca y descarga portraits y tokens para las criaturas del compendio."""
from __future__ import annotations

import json
import re
import time
import unicodedata
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageDraw

# Uses Bing Images search (no API key needed)

MODULE_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = MODULE_ROOT / "data/generated"
IMAGES_DIR = MODULE_ROOT / "images"
TOKEN_SIZE = 256
PORTRAIT_SIZE = 400


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def extract_search_terms(doc: dict) -> str:
    name = doc["name"]
    desc = doc["system"]["general"]["description"]["value"]

    paren = re.search(r"\((.+)\)", name)
    variant = paren.group(1) if paren else ""
    base_name = re.sub(r"\s*\(.*\)", "", name).strip()

    generic = {"Menor", "Mayor", "Guerrero", "Sacerdote", "Forma Elemental",
               "Forma Nioh", "Forma Yinglu", "El Rey Negro", "Antiguo",
               "Del Dolor", "Elemental mayor", "Elemental Mayor",
               "Hija de Abrael", "Espíritu Medio", "Espíritu Mayor",
               "El Señor del Infinito", "Lucifer", "Forma Dragón",
               "No muerto supremo", "Eon de las tormentas",
               "Avatar de la Guerra", "Schreckliche",
               "Schreckliche Avatar Oscuro"}

    if variant and variant not in generic:
        query = variant
    elif variant:
        query = f"{base_name} {variant}"
    else:
        query = base_name

    visual_keywords = re.findall(
        r"(?:fuego|hielo|sombra|luz|oscur\w*|drag[o\u00f3]n|serpiente|espectral|demonio|\u00e1ngel|elemental|muerto|esqueleto|fantasma|bestia|gigante|insecto|lobo|ara\u00f1a|vampir\w*|golem|caballero|guerrero|hechicero|monstruo|espiritu|planta|animal|agua|tierra|aire)",
        desc.lower()
    )
    unique_visual = list(dict.fromkeys(visual_keywords))[:2]

    parts = [query]
    parts.extend(unique_visual)
    parts.append("anime fantasy art")
    return " ".join(parts)


def search_image(query: str, max_results: int = 10) -> list[str]:
    """Search for images using Bing Images."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        url = f"https://www.bing.com/images/search?q={requests.utils.quote(query)}&form=HDRSC2&first=1"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []
        # Extract image URLs from Bing's murl attribute
        img_urls = re.findall(r"murl&quot;:&quot;(https?://[^&]+\.(?:jpg|jpeg|png|webp)[^&]*)&quot;", resp.text)
        if not img_urls:
            img_urls = re.findall(r'"murl":"(https?://[^"]+)"', resp.text)
        # Filter out tiny thumbnails and icons
        good_urls = [u for u in img_urls if "thumb" not in u.lower() and "icon" not in u.lower()]
        return good_urls[:max_results]
    except Exception as e:
        print(f"  Search error: {e}")
        return []


def download_image(url: str, timeout: int = 10) -> Image.Image | None:
    """Download an image and return as PIL Image."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
        if resp.status_code != 200:
            return None
        img = Image.open(BytesIO(resp.content))
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        return img
    except Exception:
        return None


def make_portrait(img: Image.Image, size: int = PORTRAIT_SIZE) -> Image.Image:
    """Resize and crop to square portrait."""
    w, h = img.size
    # Center crop to square
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((size, size), Image.LANCZOS)
    return img


def make_token(img: Image.Image, size: int = TOKEN_SIZE) -> Image.Image:
    """Create circular token from image."""
    portrait = make_portrait(img, size)

    # Create circular mask
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 1, size - 1), fill=255)

    # Apply mask
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(portrait, (0, 0), mask)

    # Add border
    draw = ImageDraw.Draw(result)
    draw.ellipse((0, 0, size - 1, size - 1), outline=(40, 40, 40, 255), width=3)

    return result


def get_dataset_folder(ds_id: str) -> str:
    """Map dataset ID to image folder name."""
    return slugify(ds_id)


def process_creature(doc: dict, ds_id: str, ds_label: str, location: str | None = None) -> bool:
    """Search, download and save portrait + token for a creature."""
    name = doc["name"]
    name_slug = slugify(name)

    # Determine output paths
    ds_folder = get_dataset_folder(ds_label)
    if location:
        loc_folder = slugify(location)
        portrait_dir = IMAGES_DIR / "portraits" / ds_folder / loc_folder
        token_dir = IMAGES_DIR / "tokens" / ds_folder / loc_folder
    else:
        portrait_dir = IMAGES_DIR / "portraits" / ds_folder
        token_dir = IMAGES_DIR / "tokens" / ds_folder

    portrait_path = portrait_dir / f"{name_slug}.webp"
    token_path = token_dir / f"{name_slug}_token.webp"

    # Skip if already exists
    if portrait_path.exists() and token_path.exists():
        return True

    portrait_dir.mkdir(parents=True, exist_ok=True)
    token_dir.mkdir(parents=True, exist_ok=True)

    # Search
    query = extract_search_terms(doc)
    urls = search_image(query)

    if not urls:
        # Fallback: simpler query with just the name
        base_name = re.sub(r"\s*\(.*\)", "", name).strip()
        urls = search_image(f"{base_name} fantasy anime creature art")

    # Try downloading
    for url in urls:
        img = download_image(url)
        if img is None:
            continue
        if img.size[0] < 100 or img.size[1] < 100:
            continue

        # Save portrait
        portrait = make_portrait(img)
        portrait.save(str(portrait_path), "WEBP", quality=85)

        # Save token
        token = make_token(img)
        token.save(str(token_path), "WEBP", quality=85)

        # Log attribution
        attr_path = IMAGES_DIR / "ATTRIBUTION.md"
        with open(attr_path, "a", encoding="utf-8") as f:
            f.write(f"| {name} | [{url[:60]}...]({url}) | {query} |\n")

        print(f"  OK: {name_slug}.webp")
        return True

    print(f"  FAIL: no image found for {name}")
    return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Genera portraits y tokens para criaturas.")
    parser.add_argument("--dataset", help="Solo procesar este dataset (ej: core-exxet)")
    parser.add_argument("--limit", type=int, default=0, help="Limitar a N criaturas (0=todas)")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay entre búsquedas (segundos)")
    parser.add_argument("--dry-run", action="store_true", help="Solo mostrar queries sin descargar")
    args = parser.parse_args()

    # Initialize attribution file
    attr_path = IMAGES_DIR / "ATTRIBUTION.md"
    if not attr_path.exists() or args.limit == 0:
        with open(attr_path, "w", encoding="utf-8") as f:
            f.write("# Atribución de imágenes\n\n")
            f.write("Imágenes descargadas automáticamente para uso no comercial en Foundry VTT.\n")
            f.write("Si alguna imagen infringe derechos de autor, será retirada a solicitud del titular.\n\n")
            f.write("| Criatura | URL fuente | Query de búsqueda |\n")
            f.write("|---|---|---|\n")

    index = json.load(open(GENERATED_DIR / "index.json"))
    total = 0
    ok = 0
    fail = 0

    for ds in index["datasets"]:
        if args.dataset and ds["id"] != args.dataset:
            continue

        data = json.load(open(GENERATED_DIR / ds["filename"]))
        print(f"\n=== {ds['label']} ({len(data['documents'])} criaturas) ===")

        for doc in data["documents"]:
            if args.limit and total >= args.limit:
                break

            location = doc.get("flags", {}).get("animu-exxet", {}).get("location")
            query = extract_search_terms(doc)

            if args.dry_run:
                print(f"  {doc['name'][:35]:37s} -> {query[:60]}")
                total += 1
                continue

            print(f"  [{total + 1}] {doc['name'][:35]}...", end=" ", flush=True)
            success = process_creature(doc, ds["id"], ds["label"], location)
            if success:
                ok += 1
            else:
                fail += 1
            total += 1
            time.sleep(args.delay)

        if args.limit and total >= args.limit:
            break

    print(f"\nTotal: {total} | OK: {ok} | Fail: {fail}")


if __name__ == "__main__":
    raise SystemExit(main())
