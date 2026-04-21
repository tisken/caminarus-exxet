#!/usr/bin/env python3
"""Genera un compendio de artefactos desde Prometheum Exxet."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

import plyvel

MODULE_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = MODULE_ROOT / "data/generated"
PACKS_DIR = MODULE_ROOT / "packs"
PACK_ID = "artifacts-exxet"
PACK_LABEL = "Artifacts Exxet"

PAGE_RE = re.compile(r"_Página\s+(\d+)_", re.IGNORECASE)
TAG_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
HEADING_RE = re.compile(r"^####\s+(.+)$", re.MULTILINE)
NIVEL_PODER_RE = re.compile(r"Nivel de Poder:\s*(.+?)(?:\n|$)", re.IGNORECASE)
FABULA_RE = re.compile(r"Fábula:\s*(.+?)(?:\n|$)", re.IGNORECASE)

WEAPON_TABLE_RE = re.compile(
    r"Da[\u00f1n]o\s+Turno\s+FUE\s*R\.?\s*(?:\n\s*)?"
    r"Cr[\u00ed]tico\s+1\s+Cr[\u00ed]tico\s+2\s+"
    r"(.+?)"
    r"Tipo\s+de\s+arma\s+Especial\s+Entereza\s+Rotura\s+Presencia\s+"
    r"(.+?)"
    r"Reglas\s*Especiales\s*(.+?)(?=Da[\u00f1n]o\s+Turno|Requ\.?\s*(?:de\s+)?Armadura|Nivel\s+de\s+Poder|Fábula|####|$)",
    re.IGNORECASE | re.DOTALL,
)

ARMOR_TABLE_RE = re.compile(
    r"Requ\.?\s*(?:de\s+)?Armadura\s+Pen\.?\s*Natural\s+Restr.*?Mov.*?Enter.*?Pres.*?Loca\.?\s*"
    r"(?:\n\s*)?Clase\s+(.+?)"
    r"FIL\s+CON\s+PEN\s+CAL\s+ELE\s+FRI\s+ENE"
    r"(?:\s*Reglas\s*Especiales\s*(.+?))?(?=Requ|Da[\u00f1n]o|Nivel\s+de\s+Poder|Fábula|####|$)",
    re.IGNORECASE | re.DOTALL,
)

NUMBER_RE = re.compile(r"-?\d+")
CRITIC_MAP = {
    "fil": "cut", "con": "impact", "pen": "thrust",
    "cal": "heat", "ele": "electricity", "fri": "cold", "ene": "energy",
}


def stable_id(*parts, length=16):
    return hashlib.sha1("::".join(parts).encode()).hexdigest()[:length]


def collapse(text):
    return re.sub(r"\s+", " ", text).strip()


def smart_title(text):
    stopwords = {"de", "del", "la", "el", "los", "las", "y", "o", "en", "al"}
    parts = text.lower().split()
    return " ".join(w.capitalize() if i == 0 or w not in stopwords else w for i, w in enumerate(parts))


def extract_page(text, pos):
    matches = list(PAGE_RE.finditer(text[:pos]))
    return int(matches[-1].group(1)) if matches else None


def parse_int(s):
    m = NUMBER_RE.search(re.sub(r"\s+", "", str(s or "")))
    return int(m.group(0)) if m else 0


def parse_weapon_stats(stats_line, tipo_line):
    stats_line = collapse(stats_line)
    tipo_line = collapse(tipo_line)
    nums = list(NUMBER_RE.finditer(stats_line))
    damage = int(nums[0].group(0)) if nums else 0
    turno = int(nums[1].group(0)) if len(nums) > 1 else 0
    fue_req = int(nums[2].group(0)) if len(nums) > 2 else 0
    crit1, crit2 = "-", "-"
    for key, val in CRITIC_MAP.items():
        if re.search(rf"\b{key}\b", stats_line, re.IGNORECASE):
            if crit1 == "-":
                crit1 = val
            elif crit2 == "-":
                crit2 = val
    tipo_nums = list(NUMBER_RE.finditer(tipo_line))
    entereza = int(tipo_nums[0].group(0)) if tipo_nums else 0
    rotura = int(tipo_nums[1].group(0)) if len(tipo_nums) > 1 else 0
    presencia = int(tipo_nums[2].group(0)) if len(tipo_nums) > 2 else 0
    weapon_type = re.split(r"\d", tipo_line)[0].strip()
    return {"damage": damage, "turno": turno, "fue_req": fue_req,
            "crit1": crit1, "crit2": crit2, "entereza": entereza,
            "rotura": rotura, "presencia": presencia, "weapon_type": weapon_type}


def build_stats():
    return {"systemId": "animabf", "systemVersion": "2.2.1", "coreVersion": "14.359",
            "createdTime": 1713571200000, "modifiedTime": 1713571200000,
            "lastModifiedBy": "animuExxetGen001"}


def build_weapon(name, wid, stats):
    return {"_id": wid, "name": name, "type": "weapon",
            "img": "icons/weapons/swords/greatsword-crossguard-steel.webp",
            "effects": [], "folder": None, "sort": 0, "flags": {},
            "ownership": {"default": 0}, "_stats": build_stats(), "_key": f"!items!{wid}",
            "system": {
                "special": {"value": f"Tipo: {stats['weapon_type']}"},
                "integrity": {"base": {"value": stats["entereza"]}, "final": {"value": 0}, "special": {"value": 0}},
                "breaking": {"base": {"value": stats["rotura"]}, "final": {"value": 0}, "special": {"value": 0}},
                "attack": {"base": {"value": 0}, "final": {"value": 0}, "special": {"value": 0}},
                "block": {"base": {"value": 0}, "final": {"value": 0}, "special": {"value": 0}},
                "damage": {"base": {"value": stats["damage"]}, "final": {"value": 0}, "special": {"value": 0}},
                "initiative": {"base": {"value": stats["turno"]}, "final": {"value": 0}, "special": {"value": 0}},
                "presence": {"base": {"value": stats["presencia"]}, "final": {"value": 0}, "special": {"value": 0}},
                "size": {"value": "medium"},
                "strRequired": {"oneHand": {"base": {"value": stats["fue_req"]}, "final": {"value": 0}},
                                "twoHands": {"base": {"value": 0}, "final": {"value": 0}}},
                "quality": {"value": 0}, "oneOrTwoHanded": {"value": ""},
                "knowledgeType": {"value": "known"}, "manageabilityType": {"value": "one_hand"},
                "shotType": {"value": "throw"}, "isRanged": {"value": False},
                "range": {"base": {"value": 0}, "final": {"value": 0}},
                "cadence": {"value": ""}, "reload": {"base": {"value": 0}, "final": {"value": 0}},
                "sizeProportion": {"value": "normal"},
                "weaponStrength": {"base": {"value": 0}, "final": {"value": 0}},
                "critic": {"primary": {"value": stats["crit1"]}, "secondary": {"value": stats["crit2"]}},
                "isShield": {"value": False}, "equipped": {"value": True}}}


def build_armor(name, aid):
    return {"_id": aid, "name": name, "type": "armor",
            "img": "icons/equipment/chest/breastplate-cuirass-steel-grey.webp",
            "effects": [], "folder": None, "sort": 0, "flags": {},
            "ownership": {"default": 0}, "_stats": build_stats(), "_key": f"!items!{aid}",
            "system": {
                **{k: {"base": {"value": 0}, "final": {"value": 0}, "value": 0}
                   for k in ("cut", "pierce", "impact", "thrust", "heat", "electricity", "cold", "energy")},
                "integrity": {"base": {"value": 0}, "final": {"value": 0}},
                "presence": {"base": {"value": 0}, "final": {"value": 0}},
                "movementRestriction": {"base": {"value": 0}, "final": {"value": 0}},
                "naturalPenalty": {"base": {"value": 0}, "final": {"value": 0}},
                "wearArmorRequirement": {"base": {"value": 0}, "final": {"value": 0}},
                "isEnchanted": {"value": True}, "type": {"value": "hard"},
                "localization": {"value": "complete"}, "quality": {"value": 0},
                "equipped": {"value": True}}}


def build_note(name, nid):
    return {"_id": nid, "name": name, "type": "note",
            "img": "icons/sundries/scrolls/scroll-runed-brown-purple.webp",
            "effects": [], "folder": None, "sort": 0, "flags": {},
            "ownership": {"default": 0}, "_stats": build_stats(), "_key": f"!items!{nid}",
            "system": {}}


def main():
    source_path = Path("/animu/data/docs_md/Anima Beyond Fantasy - Prometheum exxet.md")
    if not source_path.exists():
        return 1

    text = source_path.read_text(encoding="utf-8")
    start = text.find("compendio de Artefactos")
    if start == -1:
        start = 0
    scoped = text[start:]

    headings = list(HEADING_RE.finditer(scoped))
    items = []

    for i, h in enumerate(headings):
        name = smart_title(collapse(h.group(1)))
        body_start = h.end()
        body_end = headings[i + 1].start() if i + 1 < len(headings) else len(scoped)
        body = scoped[body_start:body_end]
        body_clean = TAG_COMMENT_RE.sub("", body)

        nivel_m = NIVEL_PODER_RE.search(body_clean)
        fabula_m = FABULA_RE.search(body_clean)
        if not nivel_m and not fabula_m:
            continue

        page = extract_page(scoped, h.start())

        # Count weapon and armor tables in this heading's body
        weapon_tables = list(WEAPON_TABLE_RE.finditer(body_clean))
        armor_tables = list(ARMOR_TABLE_RE.finditer(body_clean))

        # Create weapon items
        for wi, wm in enumerate(weapon_tables):
            suffix = f" ({wi + 1})" if len(weapon_tables) > 1 else ""
            wname = f"{name}{suffix}"
            wid = stable_id(PACK_ID, "w", wname)
            stats = parse_weapon_stats(wm.group(1), wm.group(2))
            items.append(("weapon", build_weapon(wname, wid, stats), page))

        # Create armor items
        for ai, am in enumerate(armor_tables):
            suffix = f" ({ai + 1})" if len(armor_tables) > 1 else ""
            aname = f"{name}{suffix}"
            aid = stable_id(PACK_ID, "a", aname)
            items.append(("armor", build_armor(aname, aid), page))

        # Always create a note with the full description
        nid = stable_id(PACK_ID, "n", name)
        note_name = f"{name} (nota)" if weapon_tables or armor_tables else name
        items.append(("note", build_note(note_name, nid), page))

    weapons = sum(1 for t, _, _ in items if t == "weapon")
    armors = sum(1 for t, _, _ in items if t == "armor")
    notes = sum(1 for t, _, _ in items if t == "note")
    print(f"Total: {len(items)} items ({weapons} armas, {armors} armaduras, {notes} notas)")

    # Build LevelDB
    ldb_dir = PACKS_DIR / PACK_ID
    if ldb_dir.exists():
        shutil.rmtree(ldb_dir)
    ldb_dir.mkdir(parents=True)
    db = plyvel.DB(str(ldb_dir), create_if_missing=True)
    sb = build_stats()

    root_id = stable_id("folder", PACK_ID, "root")
    db.put(f"!folders!{root_id}".encode(), json.dumps(
        {"color": "#000000", "name": PACK_LABEL, "sorting": "a", "type": "Item",
         "folder": None, "_id": root_id, "sort": 0, "flags": {}, "_stats": sb,
         "_key": f"!folders!{root_id}"}, ensure_ascii=False).encode())

    cat_folders = {}
    for idx, (key, label) in enumerate([("weapon", "Armas"), ("armor", "Armaduras"), ("note", "Artefactos y Notas")]):
        fid = stable_id("folder", PACK_ID, key)
        db.put(f"!folders!{fid}".encode(), json.dumps(
            {"color": "#000000", "name": label, "sorting": "a", "type": "Item",
             "folder": root_id, "_id": fid, "sort": (idx + 1) * 10, "flags": {},
             "_stats": sb, "_key": f"!folders!{fid}"}, ensure_ascii=False).encode())
        cat_folders[key] = fid

    for si, (item_type, item, page) in enumerate(items):
        item["folder"] = cat_folders[item_type]
        item["sort"] = si * 10
        db.put(item["_key"].encode(), json.dumps(item, ensure_ascii=False).encode())

    db.close()
    print(f"LevelDB en {ldb_dir}")

    index_data = [{"name": i["name"], "type": t, "page": p} for t, i, p in items]
    (OUTPUT_DIR / "artifacts-exxet.index.json").write_text(
        json.dumps(index_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
