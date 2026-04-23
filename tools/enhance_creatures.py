#!/usr/bin/env python3
"""
Mejora las criaturas del compendio:
1. Asigna tokens/portraits reales de /tmp/tokens si coinciden por nombre
2. Asigna conjuros según nivel de vía mágica
3. Asigna poderes psíquicos según disciplinas
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import unicodedata
from pathlib import Path

from PIL import Image

MODULE_ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = MODULE_ROOT / "data/generated"
IMAGES_DIR = MODULE_ROOT / "images"
TOKENS_SOURCE = Path("/tmp/tokens")
MODULE_ID = "animu-exxet"
MODULE_PREFIX = f"modules/{MODULE_ID}/images"

# Spell path name mapping (English folder names -> animabf sphere keys)
SPHERE_MAP = {
    "light": "light", "darkness": "darkness", "creation": "creation",
    "destruction": "destruction", "air": "air", "water": "water",
    "fire": "fire", "earth": "earth", "essence": "essence",
    "illusion": "illusion", "necromancy": "necromancy",
}

# Sub-path mapping
SUBPATH_MAP = {
    "sin": "darkness", "knowledge": "creation", "literature": "creation",
    "war": "destruction", "time": "essence", "death": "necromancy",
    "chaos": "destruction", "peace": "creation", "blood": "necromancy",
    "void": "darkness", "umbra": "darkness", "dreams": "illusion",
    "nobility": "light", "music": "creation",
}

# Spanish -> English sphere mapping for creature data
SPHERE_ES_TO_EN = {
    "luz": "light", "oscuridad": "darkness", "creacion": "creation",
    "creación": "creation", "destruccion": "destruction",
    "destrucción": "destruction", "aire": "air", "agua": "water",
    "fuego": "fire", "tierra": "earth", "esencia": "essence",
    "ilusion": "illusion", "ilusión": "illusion",
    "nigromancia": "necromancy", "necromancia": "necromancy",
    "vacio": "darkness", "vacío": "darkness",
}

# Psychic discipline mapping
DISCIPLINE_ES_TO_EN = {
    "telequinesis": "Psychokinesis", "piroquinesis": "Pyrokinesis",
    "crioquinesis": "Cryokinesis", "telepatia": "Telepathy",
    "telepatía": "Telepathy", "incremento fisico": "Physical Increase",
    "incremento físico": "Physical Increase",
    "sentir": "Sentience", "sentidos": "Sentience",
    "telemetria": "Telemetry", "telemetría": "Telemetry",
    "teletransporte": "Teleportation", "energia": "Energy",
    "energía": "Energy", "electromagnetismo": "Electromagnetism",
    "causalidad": "Causality", "luz": "Light",
    "hipersensibilidad": "Hypersensitivity",
    "poderes matriciales": "Matrix Powers",
}


def slugify(value):
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def normalize_for_match(name):
    """Normalize a name for fuzzy matching."""
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", name.lower())


def build_token_index():
    """Index all available images from /tmp/tokens."""
    index = {}  # normalized_name -> (token_path, portrait_path)

    for root, dirs, files in os.walk(TOKENS_SOURCE):
        for f in files:
            if not f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                continue
            path = os.path.join(root, f)
            name = os.path.splitext(f)[0]
            is_token = "_Token" in name or "_token" in name
            clean_name = name.replace("_Token", "").replace("_token", "")
            key = normalize_for_match(clean_name)

            if key not in index:
                index[key] = {"token": None, "portrait": None}

            if is_token:
                index[key]["token"] = path
            else:
                index[key]["portrait"] = path

    return index


def find_best_match(creature_name, token_index):
    """Find the best matching token for a creature name."""
    # Try exact match
    key = normalize_for_match(creature_name)
    if key in token_index:
        return token_index[key]

    # Try base name without variant
    base = re.sub(r"\s*\(.*\)", "", creature_name).strip()
    key_base = normalize_for_match(base)
    if key_base in token_index:
        return token_index[key_base]

    # Try variant only
    paren = re.search(r"\((.+)\)", creature_name)
    if paren:
        key_variant = normalize_for_match(paren.group(1))
        if key_variant in token_index:
            return token_index[key_variant]

    # Try partial match (creature name contained in token name or vice versa)
    for tk, paths in token_index.items():
        if len(tk) > 4 and (tk in key or key in tk):
            return paths
        if len(key_base) > 4 and (tk in key_base or key_base in tk):
            return paths

    return None


def convert_to_webp(src_path, dst_path, size=None):
    """Convert image to webp, optionally resize."""
    img = Image.open(src_path)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    if size:
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize((size, size), Image.LANCZOS)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(dst_path), "WEBP", quality=85)


def load_spells():
    """Load spells from the alt compendium."""
    import plyvel
    spells_dir = TOKENS_SOURCE / "anima-beyond-fantasy-alt-public-compendia/packs/spells"
    if not spells_dir.exists():
        return [], []

    db = plyvel.DB(str(spells_dir), create_if_missing=False)
    spells = []
    folders = []
    for key, value in db:
        k = key.decode("utf-8")
        obj = json.loads(value.decode("utf-8"))
        if k.startswith("!folders!"):
            folders.append(obj)
        elif k.startswith("!items!"):
            spells.append(obj)
    db.close()

    # Map folder_id -> folder_name
    folder_map = {f["_id"]: f["name"] for f in folders}

    # Assign path from folder name if not set
    for s in spells:
        if not s.get("system", {}).get("path"):
            folder_name = folder_map.get(s.get("folder"), "")
            s["system"]["path"] = folder_name

    return spells, folders


def load_psychic_powers():
    """Load psychic powers from the alt compendium."""
    import plyvel
    powers_dir = TOKENS_SOURCE / "anima-beyond-fantasy-alt-public-compendia/packs/psychic-powers"
    if not powers_dir.exists():
        return [], []

    db = plyvel.DB(str(powers_dir), create_if_missing=False)
    powers = []
    folders = []
    for key, value in db:
        k = key.decode("utf-8")
        obj = json.loads(value.decode("utf-8"))
        if k.startswith("!folders!"):
            folders.append(obj)
        elif k.startswith("!items!"):
            powers.append(obj)
    db.close()

    folder_map = {f["_id"]: f["name"] for f in folders}
    for p in powers:
        if not p.get("system", {}).get("discipline", {}).get("value"):
            folder_name = folder_map.get(p.get("folder"), "")
            p.setdefault("system", {}).setdefault("discipline", {})["value"] = folder_name

    return powers, folders


def get_creature_magic_info(doc):
    """Extract magic via levels from system data directly."""
    spheres = doc.get("system", {}).get("mystic", {}).get("magicLevel", {}).get("spheres", {})
    vias = {}
    for sphere_key, sphere_data in spheres.items():
        level = sphere_data.get("value", 0) if isinstance(sphere_data, dict) else 0
        if level > 0:
            vias[sphere_key] = level
    return vias


def get_creature_psychic_info(doc):
    """Extract psychic disciplines from creature data."""
    desc = doc["system"]["general"]["description"]["value"]
    notes = doc["system"]["general"]["notes"]
    raw = ""

    for note in notes:
        name = note.get("name", "")
        if "Disciplinas" in name or "Poderes Psíquicos" in name:
            raw += " " + name

    disc_match = re.search(r"Disciplinas.*?:</strong>\s*([^<]+)", desc)
    if disc_match:
        raw += " " + disc_match.group(1)

    disciplines = set()
    raw_lower = raw.lower()
    for es_name, en_name in DISCIPLINE_ES_TO_EN.items():
        if es_name in raw_lower:
            disciplines.add(en_name)

    return disciplines


def assign_spells_to_creature(doc, all_spells, vias):
    """Add spells to creature based on magic via levels."""
    if not vias:
        return []

    added_spells = []
    for spell in all_spells:
        spell_path = spell.get("system", {}).get("path", "").lower()
        spell_level = spell.get("system", {}).get("level", 999)
        if isinstance(spell_level, dict):
            spell_level = spell_level.get("value", 999)

        # Check main paths
        for via_en, max_level in vias.items():
            if spell_path.lower() == via_en.lower() and spell_level <= max_level:
                added_spells.append(spell)
                break

        # Check sub-paths
        for sub_en, parent_en in SUBPATH_MAP.items():
            if spell_path.lower() == sub_en.lower():
                parent_level = vias.get(parent_en, 0)
                if parent_level > 0 and spell_level <= parent_level:
                    added_spells.append(spell)
                    break

    return added_spells


def convert_alt_power_to_animabf(power, discipline_name):
    """Convert a psychicMatrix (alt format) to psychicPower (animabf format)."""
    sys = power.get("system", {})
    
    # Map effectNN fields to animabf effects structure
    effects = {}
    for threshold in ["20", "40", "80", "120", "140", "180", "240", "280", "320", "440"]:
        alt_key = f"effect{threshold}"
        alt_val = sys.get(alt_key, "")
        # Parse damage from effect text
        damage = 0
        fatigue = 0
        import re
        dmg_m = re.search(r"Damage\s+(\d+)", str(alt_val))
        fat_m = re.search(r"Fatigue\s+(\d+)", str(alt_val))
        if dmg_m:
            damage = int(dmg_m.group(1))
        if fat_m:
            fatigue = int(fat_m.group(1))
        effects[threshold] = {
            "value": str(alt_val),
            "damage": {"value": damage},
            "fatigue": {"value": fatigue},
            "shieldPoints": {"value": 0},
            "affectsInmaterial": {"value": False},
        }
    
    # Map discipline name to animabf key
    disc_key_map = {
        "Psychokinesis": "telekinesis", "Pyrokinesis": "pyrokinesis",
        "Cryokinesis": "cryokinesis", "Telepathy": "telepathy",
        "Physical Increase": "physicalIncrease", "Sentience": "sentient",
        "Telemetry": "telemetry", "Teleportation": "teleportation",
        "Energy": "energy", "Electromagnetism": "electromagnetism",
        "Causality": "causality", "Light": "light",
        "Hypersensitivity": "hypersensitivity",
        "Matrix Powers": "matrixPowers",
    }
    
    return {
        "_id": power["_id"],
        "name": power["name"],
        "type": "psychicPower",
        "img": power.get("img", "icons/svg/eye.svg"),
        "system": {
            "level": {"value": sys.get("level", 0) if isinstance(sys.get("level"), int) else 0},
            "effects": effects,
            "actionType": {"value": "active" if sys.get("action") else "passive"},
            "combatType": {"value": "attack"},
            "discipline": {"value": disc_key_map.get(discipline_name, "matrixPowers")},
            "critic": {"value": "-"},
            "hasMaintenance": {"value": str(sys.get("maint", "No")).lower() not in ("no", "0", "", "none")},
            "visible": False,
            "bonus": {"value": sys.get("bonus", 0) if isinstance(sys.get("bonus"), int) else 0},
        },
    }


def assign_psychic_to_creature(doc, all_powers, disciplines, all_folders):
    """Add psychic disciplines and powers to creature."""
    if not disciplines:
        return [], []

    added_disciplines = []
    added_powers = []
    
    # Create discipline items
    for disc_name in disciplines:
        disc_item = {
            "_id": hashlib.sha1(f"disc:{disc_name}:{doc['name']}".encode()).hexdigest()[:16],
            "name": disc_name,
            "type": "psychicDiscipline",
            "img": "icons/svg/eye.svg",
            "system": {"imbalance": False},
        }
        added_disciplines.append(disc_item)
    
    # Add powers from matching disciplines
    folder_map = {f["_id"]: f["name"] for f in all_folders}
    for power in all_powers:
        disc_name = folder_map.get(power.get("folder"), "")
        if disc_name in disciplines:
            converted = convert_alt_power_to_animabf(power, disc_name)
            added_powers.append(converted)

    return added_disciplines, added_powers


def main():
    print("=== Step 1: Building token index ===")
    token_index = build_token_index()
    print(f"Indexed {len(token_index)} token entries")

    print("\n=== Step 2: Loading spells and psychic powers ===")
    all_spells, _ = load_spells()
    all_powers, psychic_folders = load_psychic_powers()
    print(f"Spells: {len(all_spells)}, Psychic powers: {len(all_powers)}")

    print("\n=== Step 3: Processing creatures ===")
    index = json.load(open(GENERATED_DIR / "index.json"))

    token_matched = 0
    spells_added = 0
    psychic_added = 0
    total = 0

    for ds in index["datasets"]:
        data = json.load(open(GENERATED_DIR / ds["filename"]))
        ds_folder = slugify(ds["label"])

        for doc in data["documents"]:
            total += 1
            name = doc["name"]
            name_slug = slugify(name)
            location = doc.get("flags", {}).get(MODULE_ID, {}).get("location")

            # --- Token matching ---
            match = find_best_match(name, token_index)
            if match:
                if location:
                    loc_folder = slugify(location)
                    portrait_dir = IMAGES_DIR / "portraits" / ds_folder / loc_folder
                    token_dir = IMAGES_DIR / "tokens" / ds_folder / loc_folder
                else:
                    portrait_dir = IMAGES_DIR / "portraits" / ds_folder
                    token_dir = IMAGES_DIR / "tokens" / ds_folder

                # Convert and copy portrait
                if match.get("portrait"):
                    dst = portrait_dir / f"{name_slug}.webp"
                    convert_to_webp(match["portrait"], dst, size=400)
                    doc["img"] = f"{MODULE_PREFIX}/portraits/{ds_folder}/{loc_folder + '/' if location else ''}{name_slug}.webp"
                    token_matched += 1

                # Convert and copy token
                if match.get("token"):
                    dst = token_dir / f"{name_slug}_token.webp"
                    convert_to_webp(match["token"], dst, size=256)
                    doc["prototypeToken"]["texture"]["src"] = f"{MODULE_PREFIX}/tokens/{ds_folder}/{loc_folder + '/' if location else ''}{name_slug}_token.webp"
                elif match.get("portrait"):
                    # Use portrait as token too
                    dst = token_dir / f"{name_slug}_token.webp"
                    convert_to_webp(match["portrait"], dst, size=256)
                    doc["prototypeToken"]["texture"]["src"] = f"{MODULE_PREFIX}/tokens/{ds_folder}/{loc_folder + '/' if location else ''}{name_slug}_token.webp"

            # --- Spell assignment ---
            vias = get_creature_magic_info(doc)
            if vias:
                creature_spells = assign_spells_to_creature(doc, all_spells, vias)
                for spell in creature_spells:
                    # Add as embedded spell item
                    spell_item = {
                        "_id": spell["_id"],
                        "name": spell["name"],
                        "type": "spell",
                        "system": spell.get("system", {}),
                        "img": spell.get("img", "icons/svg/book.svg"),
                    }
                    # Avoid duplicates
                    existing_names = {i["name"] for i in doc.get("items", [])}
                    if spell_item["name"] not in existing_names:
                        doc.setdefault("items", []).append(spell_item)
                        spells_added += 1

            # --- Psychic power assignment ---
            disciplines = get_creature_psychic_info(doc)
            if disciplines:
                disc_items, power_items = assign_psychic_to_creature(doc, all_powers, disciplines, psychic_folders)
                existing_names = {i["name"] for i in doc.get("items", [])}
                for disc in disc_items:
                    if disc["name"] not in existing_names:
                        doc.setdefault("items", []).append(disc)
                        existing_names.add(disc["name"])
                for power in power_items:
                    if power["name"] not in existing_names:
                        doc.setdefault("items", []).append(power)
                        existing_names.add(power["name"])
                        psychic_added += 1

        # Save updated JSON
        with open(GENERATED_DIR / ds["filename"], "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

    print(f"\nResults:")
    print(f"  Total creatures: {total}")
    print(f"  Tokens matched from /tmp/tokens: {token_matched}")
    print(f"  Spells added: {spells_added}")
    print(f"  Psychic powers added: {psychic_added}")


if __name__ == "__main__":
    main()
