#!/usr/bin/env python3
"""Genera un compendio de artefactos desde Prometheum Exxet."""
from __future__ import annotations

import copy
import hashlib
import html
import json
import re
import shutil
import unicodedata
from pathlib import Path

import plyvel

MODULE_ID = "animu-exxet"
MODULE_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = MODULE_ROOT / "data/generated"
PACKS_DIR = MODULE_ROOT / "packs"
PACK_ID = "artifacts-exxet"
PACK_LABEL = "Artifacts Exxet"
SOURCE_BOOK = "Anima Beyond Fantasy - Prometheum Exxet"

HEADING_RE = re.compile(r"^####\s+(.+)$", re.MULTILINE)
PAGE_RE = re.compile(r"_Página\s+(\d+)_", re.IGNORECASE)
TAG_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
NIVEL_PODER_RE = re.compile(r"Nivel de Poder:\s*(.+?)(?:\n|$)", re.IGNORECASE)
FABULA_RE = re.compile(r"Fábula:\s*(.+?)(?:\n|$)", re.IGNORECASE)
CALIDAD_RE = re.compile(r"Calidad[:\s]+.*?\+(\d+)", re.IGNORECASE)
PRESENCIA_RE = re.compile(r"Presencia[:\s]+.*?(\d+)", re.IGNORECASE)


def stable_id(*parts: str, length: int = 16) -> str:
    return hashlib.sha1("::".join(parts).encode()).hexdigest()[:length]


def collapse_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def slugify(value: str) -> str:
    value = strip_accents(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value


def smart_title(text: str) -> str:
    stopwords = {"de", "del", "la", "el", "los", "las", "y", "o", "en", "al"}
    parts = text.lower().split()
    return " ".join(
        w.capitalize() if i == 0 or w not in stopwords else w
        for i, w in enumerate(parts)
    )


def extract_page(text: str, pos: int) -> int | None:
    matches = list(PAGE_RE.finditer(text[:pos]))
    return int(matches[-1].group(1)) if matches else None


def classify_artifact(body: str) -> str:
    lower = body.lower()
    weapon_hints = ["espada", "hacha", "lanza", "arco", "daga", "mandoble",
                    "katana", "sable", "bastón", "vara", "filo", "hoja",
                    "flecha", "virote", "pico", "martillo", "guadaña"]
    armor_hints = ["armadura", "escudo", "coraza", "yelmo", "casco",
                   "peto", "guantelete", "protección"]
    if any(h in lower for h in weapon_hints):
        return "weapon"
    if any(h in lower for h in armor_hints):
        return "armor"
    return "note"


def build_stats():
    return {
        "systemId": "animabf", "systemVersion": "2.2.1",
        "coreVersion": "14.359", "createdTime": 1713571200000,
        "modifiedTime": 1713571200000, "lastModifiedBy": "animuExxetGen001",
    }


def build_weapon_item(name: str, artifact_id: str, quality: int, body: str) -> dict:
    item_id = stable_id(artifact_id, "weapon", name)
    critic_primary = "-"
    for crit, key in [("fil", "cut"), ("con", "impact"), ("pen", "thrust"),
                      ("cal", "heat"), ("ele", "electricity"), ("fri", "cold"), ("ene", "energy")]:
        if re.search(rf"\b{crit}\b", body, re.IGNORECASE):
            critic_primary = key
            break
    return {
        "_id": item_id,
        "name": name,
        "type": "weapon",
        "img": "icons/weapons/swords/greatsword-crossguard-steel.webp",
        "effects": [], "folder": None, "sort": 0, "flags": {},
        "ownership": {"default": 0},
        "_stats": build_stats(),
        "_key": f"!items!{item_id}",
        "system": {
            "special": {"value": ""},
            "integrity": {"base": {"value": 0}, "final": {"value": 0}, "special": {"value": 0}},
            "breaking": {"base": {"value": 0}, "final": {"value": 0}, "special": {"value": 0}},
            "attack": {"base": {"value": 0}, "final": {"value": 0}, "special": {"value": 0}},
            "block": {"base": {"value": 0}, "final": {"value": 0}, "special": {"value": 0}},
            "damage": {"base": {"value": 0}, "final": {"value": 0}, "special": {"value": 0}},
            "initiative": {"base": {"value": 0}, "final": {"value": 0}, "special": {"value": 0}},
            "presence": {"base": {"value": 0}, "final": {"value": 0}, "special": {"value": 0}},
            "size": {"value": "medium"},
            "strRequired": {
                "oneHand": {"base": {"value": 0}, "final": {"value": 0}},
                "twoHands": {"base": {"value": 0}, "final": {"value": 0}},
            },
            "quality": {"value": quality},
            "oneOrTwoHanded": {"value": ""},
            "knowledgeType": {"value": "known"},
            "manageabilityType": {"value": "one_hand"},
            "shotType": {"value": "throw"},
            "isRanged": {"value": False},
            "range": {"base": {"value": 0}, "final": {"value": 0}},
            "cadence": {"value": ""},
            "reload": {"base": {"value": 0}, "final": {"value": 0}},
            "sizeProportion": {"value": "normal"},
            "weaponStrength": {"base": {"value": 0}, "final": {"value": 0}},
            "critic": {"primary": {"value": critic_primary}, "secondary": {"value": "-"}},
            "isShield": {"value": False},
            "equipped": {"value": True},
        },
    }


def build_armor_item(name: str, artifact_id: str, body: str) -> dict:
    item_id = stable_id(artifact_id, "armor", name)
    return {
        "_id": item_id,
        "name": name,
        "type": "armor",
        "img": "icons/equipment/chest/breastplate-cuirass-steel-grey.webp",
        "effects": [], "folder": None, "sort": 0, "flags": {},
        "ownership": {"default": 0},
        "_stats": build_stats(),
        "_key": f"!items!{item_id}",
        "system": {
            "cut": {"base": {"value": 0}, "final": {"value": 0}, "value": 0},
            "pierce": {"base": {"value": 0}, "final": {"value": 0}, "value": 0},
            "impact": {"base": {"value": 0}, "final": {"value": 0}, "value": 0},
            "thrust": {"base": {"value": 0}, "final": {"value": 0}, "value": 0},
            "heat": {"base": {"value": 0}, "final": {"value": 0}, "value": 0},
            "electricity": {"base": {"value": 0}, "final": {"value": 0}, "value": 0},
            "cold": {"base": {"value": 0}, "final": {"value": 0}, "value": 0},
            "energy": {"base": {"value": 0}, "final": {"value": 0}, "value": 0},
            "integrity": {"base": {"value": 0}, "final": {"value": 0}},
            "presence": {"base": {"value": 0}, "final": {"value": 0}},
            "movementRestriction": {"base": {"value": 0}, "final": {"value": 0}},
            "naturalPenalty": {"base": {"value": 0}, "final": {"value": 0}},
            "wearArmorRequirement": {"base": {"value": 0}, "final": {"value": 0}},
            "isEnchanted": {"value": True},
            "type": {"value": "hard"},
            "localization": {"value": "complete"},
            "quality": {"value": 0},
            "equipped": {"value": True},
        },
    }


def build_note_item(name: str, artifact_id: str, description: str) -> dict:
    item_id = stable_id(artifact_id, "note", name)
    return {
        "_id": item_id,
        "name": name,
        "type": "note",
        "img": "icons/sundries/scrolls/scroll-runed-brown-purple.webp",
        "effects": [], "folder": None, "sort": 0, "flags": {},
        "ownership": {"default": 0},
        "_stats": build_stats(),
        "_key": f"!items!{item_id}",
        "system": {},
    }


def extract_artifacts(source_path: Path) -> list[dict]:
    text = source_path.read_text(encoding="utf-8")
    start = text.find("compendio de Artefactos")
    if start == -1:
        start = text.find("Índice por Orden Alfabético")
    if start == -1:
        start = 0

    scoped = text[start:]
    headings = list(HEADING_RE.finditer(scoped))
    artifacts = []

    for i, m in enumerate(headings):
        name = collapse_spaces(m.group(1))
        body_start = m.end()
        body_end = headings[i + 1].start() if i + 1 < len(headings) else len(scoped)
        body = scoped[body_start:body_end].strip()
        body = TAG_COMMENT_RE.sub("", body)

        page = extract_page(scoped, m.start())
        nivel_m = NIVEL_PODER_RE.search(body)
        nivel_poder = collapse_spaces(nivel_m.group(1)) if nivel_m else None
        fabula_m = FABULA_RE.search(body)
        fabula = collapse_spaces(fabula_m.group(1)) if fabula_m else None
        calidad_m = CALIDAD_RE.search(body)
        quality = int(calidad_m.group(1)) if calidad_m else 0
        presencia_m = PRESENCIA_RE.search(body)
        presencia = int(presencia_m.group(1)) if presencia_m else 0

        item_type = classify_artifact(body)
        clean_body = re.sub(r"_Página\s+\d+_", "", body)
        clean_body = collapse_spaces(clean_body)

        if not nivel_poder and not fabula:
            continue

        artifacts.append({
            "name": smart_title(name),
            "page": page,
            "nivel_poder": nivel_poder,
            "fabula": fabula,
            "quality": quality,
            "presencia": presencia,
            "item_type": item_type,
            "body": clean_body,
            "raw_body": body,
        })

    return artifacts


def build_item_document(artifact: dict) -> dict:
    artifact_id = stable_id(PACK_ID, artifact["name"])
    item_type = artifact["item_type"]
    body = artifact["body"]
    name = artifact["name"]

    description = f"<p><strong>Fuente:</strong> {html.escape(SOURCE_BOOK)}</p>"
    if artifact["page"]:
        description += f"<p><strong>Página:</strong> {artifact['page']}</p>"
    if artifact["nivel_poder"]:
        description += f"<p><strong>Nivel de Poder:</strong> {html.escape(artifact['nivel_poder'])}</p>"
    if artifact["fabula"]:
        description += f"<p><strong>Fábula:</strong> {html.escape(artifact['fabula'])}</p>"
    description += f"<details><summary>Descripción completa</summary><p>{html.escape(body[:2000])}</p></details>"

    if item_type == "weapon":
        doc = build_weapon_item(name, artifact_id, artifact["quality"], body)
        doc["system"]["special"]["value"] = body[:500]
    elif item_type == "armor":
        doc = build_armor_item(name, artifact_id, body)
    else:
        doc = build_note_item(name, artifact_id, body)

    doc["_id"] = artifact_id
    doc["name"] = name
    doc["_key"] = f"!items!{artifact_id}"
    return doc, description


def main():
    source_path = Path("/animu/data/docs_md/Anima Beyond Fantasy - Prometheum exxet.md")
    if not source_path.exists():
        print(f"No se encontró: {source_path}")
        return 1

    artifacts = extract_artifacts(source_path)
    print(f"Artefactos extraídos: {len(artifacts)}")

    weapons = [a for a in artifacts if a["item_type"] == "weapon"]
    armors = [a for a in artifacts if a["item_type"] == "armor"]
    notes = [a for a in artifacts if a["item_type"] == "note"]
    print(f"  Armas: {weapons.__len__()}, Armaduras: {armors.__len__()}, Otros: {notes.__len__()}")

    # Build LevelDB
    ldb_dir = PACKS_DIR / PACK_ID
    if ldb_dir.exists():
        shutil.rmtree(ldb_dir)
    ldb_dir.mkdir(parents=True)

    db = plyvel.DB(str(ldb_dir), create_if_missing=True)
    stats = build_stats()

    # Root folder
    root_id = stable_id("folder", PACK_ID, "root")
    root_folder = {
        "color": "#000000", "name": PACK_LABEL, "sorting": "a",
        "type": "Item", "folder": None, "_id": root_id,
        "sort": 0, "flags": {}, "_stats": stats,
        "_key": f"!folders!{root_id}",
    }
    db.put(root_folder["_key"].encode(), json.dumps(root_folder, ensure_ascii=False).encode())

    # Category folders
    cat_folders = {}
    for idx, (cat_key, cat_name) in enumerate([("weapon", "Armas"), ("armor", "Armaduras"), ("note", "Artefactos Varios")]):
        fid = stable_id("folder", PACK_ID, cat_key)
        folder = {
            "color": "#000000", "name": cat_name, "sorting": "a",
            "type": "Item", "folder": root_id, "_id": fid,
            "sort": (idx + 1) * 10, "flags": {}, "_stats": stats,
            "_key": f"!folders!{fid}",
        }
        db.put(folder["_key"].encode(), json.dumps(folder, ensure_ascii=False).encode())
        cat_folders[cat_key] = fid

    count = 0
    for i, artifact in enumerate(artifacts):
        doc, description = build_item_document(artifact)
        doc["folder"] = cat_folders[artifact["item_type"]]
        doc["sort"] = i * 10
        db.put(doc["_key"].encode(), json.dumps(doc, ensure_ascii=False).encode())
        count += 1

    db.close()
    print(f"LevelDB compilado: {count} items en {ldb_dir}")

    # Save artifact index for reference
    index_data = [{
        "name": a["name"],
        "type": a["item_type"],
        "page": a["page"],
        "nivel_poder": a["nivel_poder"],
        "quality": a["quality"],
    } for a in artifacts]
    index_path = OUTPUT_DIR / "artifacts-exxet.index.json"
    index_path.write_text(json.dumps(index_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Índice guardado en {index_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
