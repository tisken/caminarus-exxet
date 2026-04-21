#!/usr/bin/env python3
"""Asigna portraits y tokens a los actores en los JSON generados."""
import json
import re
import unicodedata
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = MODULE_ROOT / "data/generated"
IMAGES_DIR = MODULE_ROOT / "images"
MODULE_ID = "animu-exxet"
MODULE_PREFIX = f"modules/{MODULE_ID}/images"


def slugify(value):
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def get_ds_folder(ds_label):
    return slugify(ds_label)


def main():
    index = json.load(open(GENERATED_DIR / "index.json"))
    updated = 0
    missing = 0

    for ds in index["datasets"]:
        data = json.load(open(GENERATED_DIR / ds["filename"]))
        ds_folder = get_ds_folder(ds["label"])

        for doc in data["documents"]:
            name_slug = slugify(doc["name"])
            location = doc.get("flags", {}).get(MODULE_ID, {}).get("location")

            if location:
                loc_folder = slugify(location)
                portrait_rel = f"{ds_folder}/{loc_folder}/{name_slug}.webp"
                token_rel = f"{ds_folder}/{loc_folder}/{name_slug}_token.webp"
            else:
                portrait_rel = f"{ds_folder}/{name_slug}.webp"
                token_rel = f"{ds_folder}/{name_slug}_token.webp"

            portrait_path = IMAGES_DIR / "portraits" / portrait_rel
            token_path = IMAGES_DIR / "tokens" / token_rel

            if portrait_path.exists():
                doc["img"] = f"{MODULE_PREFIX}/portraits/{portrait_rel}"
                updated += 1
            else:
                missing += 1

            if token_path.exists():
                doc["prototypeToken"]["texture"]["src"] = f"{MODULE_PREFIX}/tokens/{token_rel}"

        # Save updated JSON
        with open(GENERATED_DIR / ds["filename"], "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

    print(f"Updated: {updated}, Missing: {missing}")


if __name__ == "__main__":
    main()
