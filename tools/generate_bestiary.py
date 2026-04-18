#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import re
import shutil
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

MODULE_ID = "animu-exxet"
MODULE_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = MODULE_ROOT / "data/reference/animabf-template.json"
OUTPUT_DIR = MODULE_ROOT / "data/generated"
PACKS_DIR = MODULE_ROOT / "packs"
ANIMABF_SYSTEM_ID = "animabf"
ANIMABF_SYSTEM_VERSION = "2.2.1"
FOUNDRY_CORE_VERSION = "14.359"


def default_candidates(filename: str) -> list[Path]:
    return [
        Path("/animu/data/docs_md") / filename,
        MODULE_ROOT.parent / "data/docs_md" / filename,
    ]


BOOKS = {
    "core-exxet": {
        "label": "Core Exxet",
        "source_book": "Anima Beyond Fantasy - Core Exxet",
        "compendium_label": "Animu Exxet · Core Exxet",
        "filename": "core-exxet.actors.json",
        "records_filename": "core-exxet.records.json",
        "default_candidates": default_candidates("Anima Beyond Fantasy - Core Exxet.md"),
        "start_marker": "### Capítulo 27 Compendio de Seres",
        "end_marker": "### Reglas Adicionales",
        "mode": "headed",
    },
    "caminaron-con-nosotros": {
        "label": "Los que caminaron con nosotros",
        "source_book": "Anima Beyond Fantasy - Los que caminaron con nosotros",
        "compendium_label": "Animu Exxet · Los que caminaron con nosotros",
        "filename": "caminaron-con-nosotros.actors.json",
        "records_filename": "caminaron-con-nosotros.records.json",
        "default_candidates": default_candidates(
            "Anima Beyond Fantasy - Los que caminaron con nosotros_unlocked.md"
        ),
        "start_marker": "## Capítulo 1 hijos de Gaïa",
        "end_marker": "## Capítulo 2",
        "mode": "headed",
    },
    "complemento-web-vol-1": {
        "label": "Complemento Web Vol. 1",
        "source_book": "ABF Complemento Web Vol. 1",
        "compendium_label": "Animu Exxet · Complemento Web Vol. 1",
        "filename": "complemento-web-vol-1.actors.json",
        "records_filename": "complemento-web-vol-1.records.json",
        "default_candidates": default_candidates("ABF_Complemento_Web_Vol1.md"),
        "start_marker": "COMPENDIO",
        "end_marker": "ÍNDICE DE CONJUROS",
        "mode": "flat",
    },
    "guia-del-mundo-perfecto": {
        "label": "Guía del Mundo Perfecto",
        "source_book": "Anima Gate of Memories - Guía del Mundo Perfecto",
        "compendium_label": "Animu Exxet · Guía del Mundo Perfecto",
        "filename": "guia-del-mundo-perfecto.actors.json",
        "records_filename": "guia-del-mundo-perfecto.records.json",
        "default_candidates": default_candidates(
            "Anima Gate of Memories - Guia_del_Mundo_Perfecto.md"
        ),
        "start_marker": "ÍNDICE MARIONETAS DE LOS RECUERDOS",
        "end_marker": None,
        "mode": "flat",
        "page_title_overrides": {
            3: ["Marioneta"],
            4: ["Marioneta de Fuego"],
            5: ["Guardián de los Recuerdos"],
            7: ["Sello Defensor"],
            9: ["Noth"],
            10: ["Ophanim"],
            13: ["Noth Principado"],
            15: ["Noth Potestas"],
            19: ["Guardián del Nexo"],
            21: ["Hidra Reina"],
            22: ["Caballero Dorado"],
            25: ["Striborg"],
            27: ["Elemental Básico"],
            28: ["Pesadilla Viviente"],
            30: ["Lúgubre"],
            32: ["Marioneta de Nascal", "Marioneta de Ghestal"],
            34: ["Prototipo de Nascal"],
            37: ["Tótem Guardián"],
            39: ["Dron Menor", "Dron Mayor", "Drones de Combate de Sólomon"],
            41: ["Procasian"],
            42: ["Procasian Menor", "Procasian Mayor"],
            43: ["Dama Roja"],
            45: ["Malekith, Príncipe de los Cuervos", "Mensajeros"],
            48: ["Druaga, El Caído"],
            50: ["Jonathan Kappel"],
            52: ["Nascal"],
            54: ["El Sin Nombre"],
            56: ["Baal, La Puerta del Infierno"],
            59: ["Ergo Mundus, El Monstruo Definitivo"],
        },
    },
    "dramatis-personae": {
        "label": "Dramatis Personae",
        "source_book": "Dramatis Personae",
        "compendium_label": "Animu Exxet · Dramatis Personae",
        "filename": "dramatis-personae.actors.json",
        "records_filename": "dramatis-personae.records.json",
        "default_candidates": default_candidates("Dramatis personae.md"),
        "start_marker": "## Dramatis Personae",
        "end_marker": None,
        "mode": "flat",
        "page_title_overrides": {
            1: ["XII"],
            6: ["Kali"],
            8: ["El Coronel"],
            10: ["Anna Never"],
            12: ["Romeo Exxet"],
            16: ["Nerelas Ul del Sylvanus"],
            18: ["Griever"],
            20: ["Yuri Olson"],
            22: ["Ophiel"],
            26: ["Kujaku"],
            28: ["Alastor"],
        },
    },
    "dramatis-personae-vol-2": {
        "label": "Dramatis Personae Vol. 2",
        "source_book": "Dramatis Personae Vol. 2",
        "compendium_label": "Animu Exxet · Dramatis Personae Vol. 2",
        "filename": "dramatis-personae-vol-2.actors.json",
        "records_filename": "dramatis-personae-vol-2.records.json",
        "default_candidates": default_candidates("DramatisPersonaeVolumen2.md"),
        "start_marker": "## Dramatispersonaevolumen2",
        "end_marker": None,
        "mode": "flat",
        "page_title_overrides": {
            1: ["Balthassar, el Monstruo"],
            8: ["Killrayne, Ejecutor Imperial Supremo"],
            12: ["Ilumina, Ángel Oscuro"],
            14: ["Seline Luna, Señora de las Pesadillas"],
            18: ["Matthew Gaul, Arconte Supremo"],
            23: ["Konrad Von Rikker, Comandante de Campo de Tol Rauko"],
            26: ["Ángel Fantasma, Du Mah Type-1.000"],
            29: ["Hringham, Rey de la No Vida"],
            34: ["Valis Ul del Vilfain, Princesa de las Arias"],
            39: ["Kishidan, Caballero de la Orden del 7º Cielo"],
        },
    },
    "pantalla-del-director": {
        "label": "Pantalla del Director",
        "source_book": "Anima Pantalla del Director",
        "compendium_label": "Animu Exxet · Pantalla del Director",
        "filename": "pantalla-del-director.actors.json",
        "records_filename": "pantalla-del-director.records.json",
        "default_candidates": default_candidates("Anima_Pantalla_del_Director_unlocked.md"),
        "start_marker": "## Capítulo 3 personajesgenerados",
        "end_marker": "## Apéndice Ayudas de Juego",
        "mode": "flat",
    },
    "dravenor-parte-1": {
        "label": "Dravenor · Parte 1",
        "source_book": "DRAVENOR Ejército regular de La Máquina · Parte 1",
        "compendium_label": "Animu Exxet · Dravenor Parte 1",
        "filename": "dravenor-parte-1.actors.json",
        "records_filename": "dravenor-parte-1.records.json",
        "default_candidates": default_candidates("DRAVENOR_Ejercito_regular_de_La_Maquina_Parte_1.md"),
        "start_marker": "## Dravenorejercito Regular de la Maquina Parte 1",
        "end_marker": None,
        "mode": "flat",
        "sequential_title_overrides": [
            "Araña de Tierra (La Máquina · Varna menor)",
            "Sabueso (La Máquina · Varna menor)",
            "Alfa (La Máquina · Varna intermedia)",
            "Cangrejo (La Máquina · Varna intermedia)",
            "Colosal (La Máquina · Varna mayor)",
        ],
    },
    "dravenor-parte-2": {
        "label": "Dravenor · Parte 2",
        "source_book": "DRAVENOR Ejército regular de La Máquina · Parte 2",
        "compendium_label": "Animu Exxet · Dravenor Parte 2",
        "filename": "dravenor-parte-2.actors.json",
        "records_filename": "dravenor-parte-2.records.json",
        "default_candidates": default_candidates("DRAVENOR_Ejercito_regular_de_La_Maquina_Parte_2.md"),
        "start_marker": "## Dravenorejercito Regular de la Maquina Parte 2",
        "end_marker": None,
        "mode": "flat",
        "sequential_title_overrides": [
            "Fundidor (La Máquina · Varna intermedia)",
            "Cascarón (La Máquina · Varna menor)",
            "Camaleón (La Máquina · Varna menor)",
            "Leviatán (La Máquina · Varna intermedia)",
            "Orbe (La Máquina · Varna menor)",
        ],
    },
    "dravenor-parte-3": {
        "label": "Dravenor · Parte 3",
        "source_book": "DRAVENOR Ejército regular de La Máquina · Parte 3",
        "compendium_label": "Animu Exxet · Dravenor Parte 3",
        "filename": "dravenor-parte-3.actors.json",
        "records_filename": "dravenor-parte-3.records.json",
        "default_candidates": default_candidates("DRAVENOR_Ejercito_regular_de_La_Maquina_Parte_3.md"),
        "start_marker": "## Dravenorejercito Regular de la Maquina Parte 3",
        "end_marker": None,
        "mode": "flat",
        "sequential_title_overrides": [
            "Portador Leviatán (La Máquina · Varna mayor)",
            "Portador Abisal (La Máquina · Varna mayor)",
            "Dálcal (La Máquina · Varna suprema)",
        ],
    },
}

HEADING_RE = re.compile(r"(?m)^(#{3,4})\s+(.+?)\s*$")
PAGE_RE = re.compile(r"_Página\s+(\d+)_", re.IGNORECASE)
ORDER_RE = re.compile(r"\(order\s+#\d+\)", re.IGNORECASE)
TAG_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
LEVEL_MARKER_RE = re.compile(r"(?:[sl]?Nivel|Nivell)\s*:", re.IGNORECASE)
POINTS_MARKER_RE = re.compile(
    r"(?:Puntos\s+de\s+Vida|Putos\s+de\s+Vida|de\s+Vida|Vida)\s*:",
    re.IGNORECASE,
)
PRIMARY_STAT_RE = re.compile(
    r"Fue\s*:\s*([^\s]+).*?"
    r"Des\s*:\s*([^\s]+).*?"
    r"Agi\s*:\s*([^\s]+).*?"
    r"Con\s*:\s*([^\s]+).*?"
    r"Pod\s*:\s*([^\s]+).*?"
    r"Int\s*:\s*([^\s]+).*?"
    r"Vol\s*:\s*([^\s]+).*?"
    r"Per\s*:\s*([^\s]+)",
    re.IGNORECASE,
)
RESISTANCE_RE = re.compile(
    r"RF\s*([^\s]+).*?"
    r"RM\s*([^\s]+).*?"
    r"RP\s*([^\s]+).*?"
    r"RV\s*([^\s]+).*?"
    r"RE\s*([^\s]+)",
    re.IGNORECASE,
)
SKILL_VALUE_RE = re.compile(r"(.+?)\s+(-?\d+(?:\.\d+)?)$")
TA_VALUE_RE = re.compile(
    r"(Fil|Con|Pen|Cal|Ele|Fri|Ene)\s*(-?\d+(?:\.\d+)?)", re.IGNORECASE
)

SECONDARY_SKILL_MAP = {
    "acrobacias": ("secondaries", "athletics", "acrobatics"),
    "atletismo": ("secondaries", "athletics", "athleticism"),
    "montar": ("secondaries", "athletics", "ride"),
    "nadar": ("secondaries", "athletics", "swim"),
    "trepar": ("secondaries", "athletics", "climb"),
    "saltar": ("secondaries", "athletics", "jump"),
    "pilotar": ("secondaries", "athletics", "piloting"),
    "frialdad": ("secondaries", "vigor", "composure"),
    "proezas de fuerza": ("secondaries", "vigor", "featsOfStrength"),
    "p fuerza": ("secondaries", "vigor", "featsOfStrength"),
    "resistir el dolor": ("secondaries", "vigor", "withstandPain"),
    "res dolor": ("secondaries", "vigor", "withstandPain"),
    "advertir": ("secondaries", "perception", "notice"),
    "buscar": ("secondaries", "perception", "search"),
    "rastrear": ("secondaries", "perception", "track"),
    "rastreas": ("secondaries", "perception", "track"),
    "animales": ("secondaries", "intellectual", "animals"),
    "ciencia": ("secondaries", "intellectual", "science"),
    "ley": ("secondaries", "intellectual", "law"),
    "herbolaria": ("secondaries", "intellectual", "herbalLore"),
    "historia": ("secondaries", "intellectual", "history"),
    "tactica": ("secondaries", "intellectual", "tactics"),
    "medicina": ("secondaries", "intellectual", "medicine"),
    "memorizar": ("secondaries", "intellectual", "memorize"),
    "navegacion": ("secondaries", "intellectual", "navigation"),
    "ocultismo": ("secondaries", "intellectual", "occult"),
    "tasacion": ("secondaries", "intellectual", "appraisal"),
    "valoracion magica": ("secondaries", "intellectual", "magicAppraisal"),
    "v magica": ("secondaries", "intellectual", "magicAppraisal"),
    "estilo": ("secondaries", "social", "style"),
    "intimidar": ("secondaries", "social", "intimidate"),
    "liderazgo": ("secondaries", "social", "leadership"),
    "persuasion": ("secondaries", "social", "persuasion"),
    "comercio": ("secondaries", "social", "trading"),
    "callejeo": ("secondaries", "social", "streetwise"),
    "etiqueta": ("secondaries", "social", "etiquette"),
    "cerrajeria": ("secondaries", "subterfuge", "lockPicking"),
    "disfraz": ("secondaries", "subterfuge", "disguise"),
    "ocultarse": ("secondaries", "subterfuge", "hide"),
    "esconderse": ("secondaries", "subterfuge", "hide"),
    "robo": ("secondaries", "subterfuge", "theft"),
    "sigilo": ("secondaries", "subterfuge", "stealth"),
    "tramperia": ("secondaries", "subterfuge", "trapLore"),
    "venenos": ("secondaries", "subterfuge", "poisons"),
    "arte": ("secondaries", "creative", "art"),
    "baile": ("secondaries", "creative", "dance"),
    "forja": ("secondaries", "creative", "forging"),
    "runas": ("secondaries", "creative", "runes"),
    "alquimia": ("secondaries", "creative", "alchemy"),
    "animismo": ("secondaries", "creative", "animism"),
    "musica": ("secondaries", "creative", "music"),
    "trucos de manos": ("secondaries", "creative", "sleightOfHand"),
    "t manos": ("secondaries", "creative", "sleightOfHand"),
    "caligrafia ritual": ("secondaries", "creative", "ritualCalligraphy"),
    "orfebreria": ("secondaries", "creative", "jewelry"),
    "confeccion": ("secondaries", "creative", "tailoring"),
    "conf marionetas": ("secondaries", "creative", "puppetMaking"),
}

MAGIC_SPHERES = {
    "esencia": "essence",
    "agua": "water",
    "tierra": "earth",
    "creacion": "creation",
    "oscuridad": "darkness",
    "nigromancia": "necromancy",
    "luz": "light",
    "destruccion": "destruction",
    "aire": "air",
    "fuego": "fire",
    "ilusion": "illusion",
}

TA_DAMAGE_MAP = {
    "fil": "cut",
    "con": "impact",
    "pen": "thrust",
    "cal": "heat",
    "ele": "electricity",
    "fri": "cold",
    "ene": "energy",
}

UI_SETTING_KEYWORDS = {
    "inhuman": ("inhumanidad",),
    "zen": ("zen",),
    "inmaterial": ("exencion fisica", "espiritus", "forma elemental"),
    "perceiveMystic": ("ver lo sobrenatural", "ver magia", "ver espiritus"),
    "perceivePsychic": ("ver lo sobrenatural", "ver matrices"),
}

RECORD_OVERRIDES = {
    ("core-exxet", "Nezuacuatil", 5, 321, 1): {
        "variant": "Enjambre de cucarachas",
    },
    ("core-exxet", "Dragón", 7, 328, 1): {
        "variant": "Menor",
    },
    ("core-exxet", "Dragón", 9, 328, 2): {
        "variant": "Mayor",
    },
    ("core-exxet", "Zombi", 11, 329, 1): {
        "source_heading": "Dragón",
        "variant": "Antiguo",
    },
    ("core-exxet", "Zombi", 0, 329, 2): {
        "variant": None,
    },
    ("core-exxet", "Degollador", 5, 330, 1): {
        "variant": "Quimera no muerta",
    },
    ("core-exxet", "Filisnogos", 4, 331, 1): {
        "variant": "Espíritu de la caza",
    },
    ("core-exxet", "Filisnogos", 15, 331, 2): {
        "variant": "Venganza de la antigüedad",
    },
    ("core-exxet", "Señor de las Tinieblas", 10, 333, 2): {
        "variant": "Elemental mayor",
    },
    ("caminaron-con-nosotros", "Balzak", 2, 25, 1): {
        "variant": "Guerrero",
    },
    ("caminaron-con-nosotros", "Balzak", 2, 25, 2): {
        "variant": "Sacerdote",
    },
    ("caminaron-con-nosotros", "Behemoth", 11, 28, 1): {
        "variant": "Soberano de las bestias del mundo",
    },
    ("caminaron-con-nosotros", "Belphe", 10, 30, 1): {
        "variant": "Elemental mayor",
    },
    ("caminaron-con-nosotros", "Belphe", 8, 30, 1): {
        "variant": "Elemental mayor",
    },
    ("caminaron-con-nosotros", "Esfinge", 6, 68, 1): {
        "variant": None,
    },
    ("caminaron-con-nosotros", "Esfinge", 7, 68, 1): {
        "variant": None,
    },
    ("caminaron-con-nosotros", "Tecnócrita", 6, 98, 1): {
        "variant": "La máquina",
    },
    ("caminaron-con-nosotros", "Portador", 3, 108, 1): {
        "variant": "Menor",
    },
    ("caminaron-con-nosotros", "Portador", 7, 99, 1): {
        "variant": "Menor",
    },
    ("caminaron-con-nosotros", "Portador", 8, 99, 2): {
        "variant": "Mayor",
    },
    ("caminaron-con-nosotros", "Orbe del Infinito", 15, 123, 1): {
        "variant": "El fragmento del mundo",
    },
    ("caminaron-con-nosotros", "Orbe del Infinito", 14, 130, 1): {
        "variant": "El fragmento del mundo",
    },
    ("caminaron-con-nosotros", "Señor de los Muertos", 17, 138, 1): {
        "variant": None,
    },
    ("caminaron-con-nosotros", "Señor de los Muertos", 10, 151, 1): {
        "variant": "No muerto supremo",
    },
    ("caminaron-con-nosotros", "Rudraskha", 15, 142, 1): {
        "variant": "Eon de las tormentas",
    },
}


def collapse_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_digit_spacing(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"(?<=\d)\s+\.(?=\d)", ".", text)
    text = re.sub(r"(?<=\d)\.\s+(?=\d)", ".", text)
    text = re.sub(r"(?<=\d)\s+(?=\d)", "", text)
    text = re.sub(r"(?<=\+)\s+(?=\d)", "", text)
    return text


def normalize_flat(text: str) -> str:
    text = TAG_COMMENT_RE.sub(" ", text)
    text = ORDER_RE.sub(" ", text)
    text = normalize_digit_spacing(text)
    text = text.replace("\n", " ")
    return collapse_spaces(text)


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn")


def normalize_key(value: str) -> str:
    value = strip_accents(value).lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return collapse_spaces(value)


def slugify(value: str) -> str:
    return normalize_key(value).replace(" ", "-")


def merge_ocr_title_fragments(text: str) -> str:
    tokens = re.findall(r"[A-Za-zÀ-ÿ0-9'-]+", text)
    if not tokens:
        return ""

    merged: list[str] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        lower = token.islower()

        if lower and len(token) == 1 and index + 1 < len(tokens):
            token = token + tokens[index + 1]
            index += 1

        if (
            merged
            and token.islower()
            and len(token) <= 2
            and normalize_key(token) not in {"de", "del", "la", "el", "los", "las", "y", "o", "en"}
            and merged[-1].islower()
        ):
            merged[-1] += token
        elif (
            merged
            and len(token) <= 3
            and token[:1].isupper()
            and token[1:].islower()
            and merged[-1].islower()
        ):
            merged[-1] += token.lower()
        else:
            merged.append(token)

        index += 1

    return " ".join(merged)


def parse_int(value: str | None) -> int | None:
    if not value:
        return None
    match = NUMBER_RE.search(normalize_digit_spacing(value))
    if not match:
        return None
    return int(match.group(0).replace(".", ""))


def parse_all_ints(value: str | None) -> list[int]:
    if not value:
        return []
    return [int(match.group(0).replace(".", "")) for match in NUMBER_RE.finditer(normalize_digit_spacing(value))]


def safe_stat(value: str | None) -> int:
    parsed = parse_int(value)
    return parsed if parsed is not None else 0


def calculate_attribute_modifier(value: int) -> int:
    if value <= 0:
        return 0
    if value < 4:
        return value * 10 - 40
    return min(
        (
            ((value + 5) // 5)
            + ((value + 4) // 5)
            + ((value + 2) // 5)
            - 4
        )
        * 5,
        45,
    )


def calculate_regeneration_type_from_constitution(constitution: int) -> int:
    constitution = max(min(constitution, 20), 0)
    if constitution <= 2:
        return 0
    if constitution <= 7:
        return 1
    if constitution <= 9:
        return 2
    if constitution == 20:
        return 12
    return constitution - 7


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_stats_block() -> dict:
    return {
        "systemId": ANIMABF_SYSTEM_ID,
        "systemVersion": ANIMABF_SYSTEM_VERSION,
        "coreVersion": FOUNDRY_CORE_VERSION,
        "createdTime": None,
        "modifiedTime": None,
        "lastModifiedBy": None,
    }


def stable_id(*parts: str, length: int = 16) -> str:
    digest = hashlib.sha1("::".join(parts).encode("utf-8")).hexdigest()
    return digest[:length]


def pack_filename(document: dict) -> str:
    base_name = slugify(document.get("name", "entry")).replace("-", "_")[:80] or "entry"
    return f"{document['type']}_{base_name}_{document['_id']}.json"


def write_pack_source(book_id: str, documents: list[dict]) -> None:
    pack_dir = PACKS_DIR / book_id
    if pack_dir.exists():
        shutil.rmtree(pack_dir)
    pack_dir.mkdir(parents=True, exist_ok=True)

    for document in documents:
        write_json(pack_dir / pack_filename(document), document)


def discover_path(explicit: str | None, candidates: list[Path]) -> Path:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if path.exists():
            return path
        raise FileNotFoundError(f"No existe la ruta indicada: {path}")

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    raise FileNotFoundError(
        "No se encontró el manual fuente en ninguna de las rutas candidatas."
    )


def slice_section(text: str, start_marker: str, end_marker: str | None) -> str:
    start = text.find(start_marker)
    if start == -1:
        raise ValueError(f"No se encontró el marcador de inicio: {start_marker}")
    start += len(start_marker)

    end = text.find(end_marker, start) if end_marker else -1
    if end == -1:
        end = len(text)
    return text[start:end].strip()


def iter_sections(text: str) -> list[dict]:
    matches = list(HEADING_RE.finditer(text))
    sections = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append(
            {
                "level": len(match.group(1)),
                "title": collapse_spaces(match.group(2)),
                "body": text[start:end].strip(),
            }
        )
    return sections


def find_profile_windows(section_body: str) -> list[tuple[int, int]]:
    matches = list(LEVEL_MARKER_RE.finditer(section_body))
    if not matches:
        return []

    windows = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section_body)
        windows.append((start, end))
    return windows


def extract_page(section_body: str, position: int) -> int | None:
    matches = list(PAGE_RE.finditer(section_body[:position]))
    if not matches:
        return None
    return int(matches[-1].group(1))


def cleanup_variant_label(section_title: str, candidate: str) -> str | None:
    candidate = TAG_COMMENT_RE.sub(" ", candidate)
    candidate = PAGE_RE.sub(" ", candidate)
    candidate = ORDER_RE.sub(" ", candidate)
    candidate = collapse_spaces(candidate)
    candidate = merge_ocr_title_fragments(candidate)
    candidate = collapse_spaces(candidate)

    if not candidate:
        return None

    tokens = candidate.split()
    normalized_title = normalize_key(section_title)
    normalized_title_dense = normalized_title.replace(" ", "")
    for count in range(1, min(4, len(tokens)) + 1):
        prefix_spaced = normalize_key(" ".join(tokens[:count]))
        prefix_dense = prefix_spaced.replace(" ", "")
        if prefix_spaced == normalized_title or prefix_dense == normalized_title_dense:
            tokens = tokens[count:]
            candidate = " ".join(tokens)
            break

    candidate = candidate.strip(" -,:;.")
    if not candidate:
        return None
    if normalize_key(candidate) == normalized_title:
        return None
    if len(candidate.split()) > 7:
        return None
    return smart_title(candidate)


def smart_title(text: str) -> str:
    lowered = text.lower()
    parts = re.split(r"(\s+)", lowered)
    stopwords = {"de", "del", "la", "el", "los", "las", "y", "o", "en", "al"}
    titled: list[str] = []
    seen_word = False
    for part in parts:
        if not part or part.isspace():
            titled.append(part)
            continue
        token_key = normalize_key(part)
        if seen_word and token_key in stopwords:
            titled.append(part)
        else:
            titled.append(part.capitalize())
        seen_word = True
    return "".join(titled)


def extract_variant(section_title: str, section_body: str, position: int) -> str | None:
    window = section_body[max(0, position - 220) : position]
    window = TAG_COMMENT_RE.sub("\n", window)
    window = PAGE_RE.sub("\n", window)
    lines = [collapse_spaces(line) for line in window.splitlines() if collapse_spaces(line)]
    if not lines:
        return None
    return cleanup_variant_label(section_title, lines[-1])


def extract_flat_title(source_text: str, position: int) -> str | None:
    window = source_text[max(0, position - 180) : position]
    window = TAG_COMMENT_RE.sub("\n", window)
    window = PAGE_RE.sub("\n", window)
    window = ORDER_RE.sub("\n", window)
    window = re.sub(r"(?<=[a-záéíóúüñ])(?=[A-ZÁÉÍÓÚÜÑ])", " ", window)
    window = re.sub(r"(?<=\d)(?=[A-Za-zÀ-ÿ])", " ", window)

    lines = [collapse_spaces(line) for line in window.splitlines() if collapse_spaces(line)]
    candidate = lines[-1] if lines else collapse_spaces(window)
    candidate = re.sub(r"^#+\s*", "", candidate)
    candidate = re.sub(
        r".*(?:Descripci[óo]n|Posesiones|Consejos de interpretaci[óo]n|Notas y curiosidades)\s*:\s*",
        "",
        candidate,
        flags=re.IGNORECASE,
    )
    if "indice" in normalize_key(candidate):
        candidate = re.split(r"ÍNDICE", candidate, flags=re.IGNORECASE)[-1]
    else:
        fragments = [fragment.strip() for fragment in re.split(r"[.!?]", candidate) if fragment.strip()]
        if fragments:
            candidate = fragments[-1]

    digit_fragments = [fragment.strip() for fragment in re.split(r"\d+", candidate) if fragment.strip()]
    if digit_fragments:
        tail = digit_fragments[-1]
        if re.search(r"[A-Za-zÀ-ÿ]", tail):
            candidate = tail

    tokens = re.findall(r"[A-Za-zÀ-ÿ'´`-]+", candidate)
    if not tokens:
        return None

    candidate = " ".join(tokens[-8:])
    candidate = merge_ocr_title_fragments(candidate)
    candidate = collapse_spaces(candidate.strip(" -,:;."))
    if not candidate:
        return None

    return smart_title(candidate)


def extract_labeled_fields(chunk: str) -> dict[str, str]:
    flat = normalize_flat(chunk)
    patterns = {
        "level": r"(?:[sl]?Nivel|Nivell)\s*:",
        "points": r"(?:Puntos\s+de\s+Vida|Putos\s+de\s+Vida|de\s+Vida|Vida)\s*:",
        "class": r"Clase\s*:",
        "category": r"(?:Categor[íi]a|Profesi[óo]n)\s*:",
        "race": r"Raza\s*:",
        "turn": r"(?:Turno|Iniciativa)\s*:",
        "attack": r"(?:Habilidad|Hab\.)\s+de\s+ataque\s*:",
        "defense": r"(?:Habilidad|Hab\.)\s+de\s+(?:defensa|esquiva)\s*:",
        "damage": r"(?:Da[ñn]o|Damage)\s*:",
        "wear_armor": r"Llevar\s+armadura\s*:",
        "ta": r"TA\s*:",
        "act": r"(?:ACT|Act)\s*:",
        "zeon": r"Zeon\s*:",
        "magic_projection": r"Proyecci[óo]n\s+M[áa]gica\s*:",
        "magic_level": r"Nivel\s+de\s+magia\s*:",
        "summon": r"Convocar\s*:",
        "control": r"(?:Dominaci[óo]n|Control(?:ar)?)\s*:",
        "bind": r"(?:Atadura|Atar)\s*:",
        "banish": r"Desconvocar\s*:",
        "psychic_potential": r"Potencial(?:\s+Ps[íi]quico)?\s*:",
        "cv": r"CVs?\s*Libres\s*:",
        "disciplines": r"Disciplinas(?:\s*:)?",
        "innate": r"Innatos\s*:",
        "psychic_projection": r"Proyecci[óo]n\s+Ps[íi]quica\s*:",
        "psychic_powers": r"Poderes\s+Ps[íi]quicos\s*:",
        "natural_abilities": r"Habilidades\s+naturales\s*:",
        "essentials": r"Habilidades\s+esenciales\s*:",
        "powers": r"Poderes(?!\s+Ps[íi]quicos)\s*:",
        "advantages": r"Ventajas\s+y\s+desventajas\s*:",
        "ki": r"Ki\s*:",
        "accumulations": r"Acumulaciones(?:\s+de\s+Ki)?\s*:",
        "techniques": r"T[ée]cnicas\s*:",
        "martial_arts": r"Artes\s+Marciales\s*:",
        "invocations": r"Invocaciones\s*:",
        "metamagic": r"Metamagia\s*:",
        "elan": r"Elan\s*:",
        "size": r"Tama[ñn]o\s*:",
        "regen": r"Regeneraci[óo]n\s*:",
        "movement": r"(?:Tipo\s+de\s+movimiento|de\s+movimiento)\s*:",
        "fatigue": r"Cansancio\s*:",
        "secondary_skills": r"Habilidades\s+Secundarias\s*:",
    }

    positions = []
    for key, pattern in patterns.items():
        match = re.search(pattern, flat, flags=re.IGNORECASE)
        if match:
            positions.append((match.start(), match.end(), key))

    positions.sort(key=lambda item: item[0])
    fields: dict[str, str] = {}
    for index, (_, end, key) in enumerate(positions):
        next_start = positions[index + 1][0] if index + 1 < len(positions) else len(flat)
        fields[key] = collapse_spaces(flat[end:next_start])
    return fields


def split_level_and_class(level_fragment: str) -> tuple[int | None, str | None, int | None]:
    level_fragment = collapse_spaces(level_fragment)
    level_value = parse_int(level_fragment)
    class_fragment = level_fragment

    if "clase:" in level_fragment.lower():
        class_fragment = re.split(r"Clase\s*:", level_fragment, flags=re.IGNORECASE)[-1]
    elif level_value is not None:
        match = NUMBER_RE.search(normalize_digit_spacing(level_fragment))
        if match:
            class_fragment = level_fragment[match.end() :].strip(" ,;")

    gnosis = None
    normalized = normalize_digit_spacing(class_fragment)
    gnosis_match = re.search(r"(.+?)\s+(-?\d+(?:\.\d+)?)$", normalized)
    if gnosis_match:
        class_fragment = gnosis_match.group(1).strip(" ,;")
        gnosis = parse_int(gnosis_match.group(2))

    return level_value, class_fragment or None, gnosis


def parse_primary_stats(fields: dict[str, str]) -> dict[str, int]:
    joined = " ".join(
        fields.get(key, "")
        for key in ["class", "category", "race", "turn", "attack", "defense", "damage", "ta"]
    )
    match = PRIMARY_STAT_RE.search(normalize_flat(joined))
    if not match:
        return {}
    return {
        "strength": safe_stat(match.group(1)),
        "dexterity": safe_stat(match.group(2)),
        "agility": safe_stat(match.group(3)),
        "constitution": safe_stat(match.group(4)),
        "power": safe_stat(match.group(5)),
        "intelligence": safe_stat(match.group(6)),
        "willPower": safe_stat(match.group(7)),
        "perception": safe_stat(match.group(8)),
    }


def parse_resistances(fields: dict[str, str]) -> dict[str, int]:
    joined = " ".join(
        fields.get(key, "")
        for key in ["class", "category", "race", "turn", "attack", "defense", "damage", "ta"]
    )
    match = RESISTANCE_RE.search(normalize_flat(joined))
    if not match:
        return {}
    return {
        "physical": safe_stat(match.group(1)),
        "magic": safe_stat(match.group(2)),
        "psychic": safe_stat(match.group(3)),
        "disease": safe_stat(match.group(4)),
        "poison": safe_stat(match.group(5)),
    }


def infer_defense_mode(defense_raw: str | None) -> str:
    if not defense_raw:
        return "none"
    normalized = normalize_key(defense_raw)
    if "acumulacion" in normalized:
        return "accumulation"
    if "esquiva" in normalized or "defensa fantasmal" in normalized:
        return "dodge"
    return "block"


def parse_secondary_skills(raw_value: str | None) -> tuple[str, dict[tuple[str, ...], int], str | None]:
    if not raw_value:
        return "", {}, None

    flat = collapse_spaces(raw_value)
    narrative = None
    period_match = re.search(r"\.\s+(?=[A-ZÁÉÍÓÚÜÑ\"“(])", flat)
    if period_match:
        skills_text = flat[: period_match.start()]
        narrative = flat[period_match.end() :].strip()
    else:
        skills_text = flat.rstrip(".")

    parsed: dict[tuple[str, ...], int] = {}
    for part in [segment.strip() for segment in skills_text.split(",") if segment.strip()]:
        cleaned = re.sub(r"\([^)]*\)", "", part).strip()
        cleaned = collapse_spaces(normalize_digit_spacing(cleaned))
        match = SKILL_VALUE_RE.match(cleaned)
        if not match:
            continue
        label = normalize_key(match.group(1))
        label = label.replace("  ", " ")
        value = parse_int(match.group(2))
        if value is None:
            continue

        if label in SECONDARY_SKILL_MAP:
            parsed[SECONDARY_SKILL_MAP[label]] = value

    return skills_text.strip(), parsed, narrative


def parse_ta_values(ta_raw: str | None) -> dict[str, int]:
    if not ta_raw:
        return {}
    ta_raw = normalize_digit_spacing(ta_raw)
    matches = TA_VALUE_RE.findall(ta_raw)
    if matches:
        values = {}
        for damage_type, value in matches:
            values[TA_DAMAGE_MAP[normalize_key(damage_type)]] = parse_int(value) or 0
        return values

    if normalize_key(ta_raw) in {"ninguna", "na"}:
        return {}

    uniform = parse_int(ta_raw)
    if uniform is None:
        return {}

    return {
        "cut": uniform,
        "impact": uniform,
        "thrust": uniform,
        "heat": uniform,
        "electricity": uniform,
        "cold": uniform,
        "energy": uniform,
    }


def build_armor_item(name: str, ta_raw: str | None) -> dict | None:
    values = parse_ta_values(ta_raw)
    if not values:
        return None

    item_name = "Armadura natural"
    if ta_raw:
        prefix = re.split(r"(Fil|Con|Pen|Cal|Ele|Fri|Ene)\s*\d", ta_raw, maxsplit=1, flags=re.IGNORECASE)[0]
        prefix = collapse_spaces(prefix.strip(" :;,."))
        if prefix and normalize_key(prefix) not in {"natural", "ta"}:
            item_name = prefix

    highest_armor = max(values.values())
    presence = max(5, 20 + highest_armor * 5)
    integrity = max(5, 10 + highest_armor * 2)

    def armor_value(key: str) -> int:
        return values.get(key, 0)

    return {
        "name": item_name,
        "type": "armor",
        "img": "icons/equipment/chest/breastplate-cuirass-steel-grey.webp",
        "effects": [],
        "system": {
            "cut": {"base": {"value": armor_value("cut")}, "final": {"value": 0}, "value": armor_value("cut")},
            "pierce": {"base": {"value": 0}, "final": {"value": 0}, "value": 0},
            "impact": {"base": {"value": armor_value("impact")}, "final": {"value": 0}, "value": armor_value("impact")},
            "thrust": {"base": {"value": armor_value("thrust")}, "final": {"value": 0}, "value": armor_value("thrust")},
            "heat": {"base": {"value": armor_value("heat")}, "final": {"value": 0}, "value": armor_value("heat")},
            "electricity": {
                "base": {"value": armor_value("electricity")},
                "final": {"value": 0},
                "value": armor_value("electricity"),
            },
            "cold": {"base": {"value": armor_value("cold")}, "final": {"value": 0}, "value": armor_value("cold")},
            "energy": {"base": {"value": armor_value("energy")}, "final": {"value": 0}, "value": armor_value("energy")},
            "integrity": {"base": {"value": integrity}, "final": {"value": 0}, "value": integrity},
            "presence": {"base": {"value": presence}, "final": {"value": 0}, "value": presence},
            "movementRestriction": {"base": {"value": 0}, "final": {"value": 0}},
            "naturalPenalty": {"base": {"value": 0}, "final": {"value": 0}, "value": 0},
            "wearArmorRequirement": {"base": {"value": 0}, "final": {"value": 0}, "value": 0},
            "type": {"value": "hard"},
            "localization": {"value": "breastplate"},
            "isEnchanted": {"value": False},
            "quality": {"value": 0},
            "equipped": {"value": True},
        },
    }


def html_paragraph(text: str | None) -> str:
    if not text:
        return ""
    escaped = html.escape(text)
    return f"<p>{escaped}</p>"


def is_viable_record(record: dict) -> bool:
    if not record.get("life_points"):
        return False
    if not record.get("primary_stats"):
        return False
    if not record.get("resistances"):
        return False

    normalized_name = normalize_key(record.get("name", ""))
    if not normalized_name:
        return False
    if normalized_name in {"nivel", "cm", "efectos"}:
        return False
    return True


def build_description(record: dict) -> str:
    source_bits = [
        f"<p><strong>Fuente:</strong> {html.escape(record['source_book'])}</p>",
    ]
    if record.get("page"):
        source_bits.append(f"<p><strong>Página:</strong> {record['page']}</p>")
    if record.get("source_heading"):
        source_bits.append(
            f"<p><strong>Entrada:</strong> {html.escape(record['source_heading'])}</p>"
        )
    if record.get("variant"):
        source_bits.append(
            f"<p><strong>Variante:</strong> {html.escape(record['variant'])}</p>"
        )

    summary_bits = []
    if record.get("race"):
        summary_bits.append(
            f"<p><strong>Raza:</strong> {html.escape(record['race'])}</p>"
        )
    if record.get("creature_class"):
        summary_bits.append(
            f"<p><strong>Clase:</strong> {html.escape(record['creature_class'])}</p>"
        )
    if record.get("category"):
        summary_bits.append(
            f"<p><strong>Categoría:</strong> {html.escape(record['category'])}</p>"
        )
    if record.get("advantages"):
        summary_bits.append(
            f"<p><strong>Ventajas y desventajas:</strong> {html.escape(record['advantages'])}</p>"
        )
    if record.get("natural_abilities"):
        summary_bits.append(
            f"<p><strong>Habilidades naturales:</strong> {html.escape(record['natural_abilities'])}</p>"
        )
    if record.get("essentials"):
        summary_bits.append(
            f"<p><strong>Habilidades esenciales:</strong> {html.escape(record['essentials'])}</p>"
        )
    if record.get("powers"):
        summary_bits.append(
            f"<p><strong>Poderes:</strong> {html.escape(record['powers'])}</p>"
        )
    if record.get("disciplines"):
        summary_bits.append(
            f"<p><strong>Disciplinas:</strong> {html.escape(record['disciplines'])}</p>"
        )
    if record.get("damage_raw"):
        summary_bits.append(
            f"<p><strong>Daño:</strong> {html.escape(record['damage_raw'])}</p>"
        )
    if record.get("ta_raw"):
        summary_bits.append(
            f"<p><strong>TA:</strong> {html.escape(record['ta_raw'])}</p>"
        )
    if record.get("secondary_skills_raw"):
        summary_bits.append(
            f"<p><strong>Habilidades secundarias:</strong> {html.escape(record['secondary_skills_raw'])}</p>"
        )
    if record.get("narrative"):
        summary_bits.append(
            f"<p><strong>Descripción breve:</strong> {html.escape(record['narrative'])}</p>"
        )
    if record.get("warnings"):
        summary_bits.append(
            f"<p><strong>Avisos de extracción:</strong> {html.escape('; '.join(record['warnings']))}</p>"
        )

    raw_chunk = html.escape(record["raw_chunk"].strip())
    raw_block = f"<details><summary>Texto extraído</summary><pre>{raw_chunk}</pre></details>"

    return "".join(
        [
            "<section><h2>Fuente</h2>",
            *source_bits,
            "</section>",
            "<section><h2>Resumen importado</h2>",
            *summary_bits,
            "</section>",
            raw_block,
        ]
    )


def set_secondary_value(system: dict, path: tuple[str, ...], value: int) -> None:
    node = system
    for key in path:
        node = node[key]
    node["base"] = {"value": value}


def infer_sphere_levels(raw_value: str | None) -> dict[str, int]:
    if not raw_value:
        return {}
    found: dict[str, int] = {}
    for sphere_label, sphere_key in MAGIC_SPHERES.items():
        match = re.search(
            rf"{sphere_label}\s*(-?\d+(?:\.\d+)?)",
            normalize_key(raw_value),
            flags=re.IGNORECASE,
        )
        if match:
            found[sphere_key] = parse_int(match.group(1)) or 0
    return found


def apply_ui_flags(system: dict, joined_text: str) -> None:
    normalized = normalize_key(joined_text)
    for key, keywords in UI_SETTING_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            system["general"]["settings"][key]["value"] = True


NOTE_FIELDS = [
    ("advantages", "Ventajas y desventajas"),
    ("natural_abilities", "Habilidades naturales"),
    ("essentials", "Habilidades esenciales"),
    ("powers", "Poderes"),
    ("psychic_powers", "Poderes psíquicos"),
    ("disciplines", "Disciplinas"),
    ("ki", "Ki"),
    ("accumulations", "Acumulaciones"),
    ("techniques", "Técnicas"),
    ("martial_arts", "Artes marciales"),
    ("invocations", "Invocaciones"),
    ("metamagic", "Metamagia"),
    ("elan", "Elan"),
]


def build_note_entries(record: dict) -> list[dict]:
    notes = []
    base_slug = slugify(record.get("name", "criatura"))[:32] or "criatura"
    for index, (field_name, label) in enumerate(NOTE_FIELDS, start=1):
        raw_value = collapse_spaces(record.get(field_name) or "")
        if not raw_value:
            continue
        notes.append(
            {
                "_id": f"note-{base_slug}-{index}",
                "type": "note",
                "name": f"{label}: {raw_value}",
                "system": {},
            }
        )
    return notes


def build_actor_document(record: dict, template: dict) -> dict:
    actor_id = stable_id(record["id"])
    system = copy.deepcopy(template["Actor"]["character"])
    stats = record["primary_stats"]
    resistances = record["resistances"]

    level = record.get("level") or 0
    presence_base = 20 if level <= 0 else 25 + level * 5

    for key, value in (
        ("agility", stats.get("agility", 0)),
        ("constitution", stats.get("constitution", 0)),
        ("dexterity", stats.get("dexterity", 0)),
        ("strength", stats.get("strength", 0)),
        ("intelligence", stats.get("intelligence", 0)),
        ("perception", stats.get("perception", 0)),
        ("power", stats.get("power", 0)),
        ("willPower", stats.get("willPower", 0)),
    ):
        system["characteristics"]["primaries"][key]["base"] = {"value": value}

    system["general"]["level"]["value"] = level
    system["general"]["levels"] = [
        {
            "_id": f"lvl-{slugify(record['name'])[:24] or 'creature'}",
            "type": "level",
            "name": record["name"],
            "flags": {"version": 1},
            "system": {"level": level},
        }
    ]
    system["general"]["presence"]["special"]["value"] = 0
    system["general"]["aspect"]["race"]["value"] = (
        record.get("race") or record.get("creature_class") or ""
    )
    system["general"]["aspect"]["appearance"]["value"] = record.get("variant") or ""
    system["general"]["aspect"]["size"]["value"] = record.get("size_value") or 0
    system["general"]["description"]["value"] = build_description(record)
    system["general"]["notes"] = build_note_entries(record)

    life_points = record.get("life_points") or 0
    fatigue = record.get("fatigue") or 0
    initiative = record.get("initiative") or 0
    movement = record.get("movement") or 0
    regeneration = record.get("regeneration") or 0
    wear_armor = record.get("wear_armor") or 0

    system["characteristics"]["secondaries"]["lifePoints"]["value"] = life_points
    system["characteristics"]["secondaries"]["lifePoints"]["max"] = life_points
    system["characteristics"]["secondaries"]["fatigue"]["value"] = fatigue
    system["characteristics"]["secondaries"]["fatigue"]["max"] = fatigue
    system["characteristics"]["secondaries"]["initiative"]["base"]["value"] = initiative
    system["characteristics"]["secondaries"]["movementType"]["mod"]["value"] = (
        movement - stats.get("agility", 0)
    )
    system["characteristics"]["secondaries"]["regenerationType"]["mod"]["value"] = (
        regeneration - calculate_regeneration_type_from_constitution(stats.get("constitution", 0))
    )

    resistance_map = {
        "physical": ("constitution", "physical"),
        "disease": ("constitution", "disease"),
        "poison": ("constitution", "poison"),
        "magic": ("power", "magic"),
        "psychic": ("willPower", "psychic"),
    }
    for resistance_key, (attribute_key, manual_key) in resistance_map.items():
        base = presence_base + calculate_attribute_modifier(stats.get(attribute_key, 0))
        final = resistances.get(manual_key, base)
        system["characteristics"]["secondaries"]["resistances"][resistance_key]["special"] = {
            "value": final - base
        }

    for path, value in record.get("secondary_skills", {}).items():
        set_secondary_value(system, path, value)

    attack_value = record.get("attack")
    defense_value = record.get("defense")
    defense_mode = record.get("defense_mode")
    if attack_value is not None:
        system["combat"]["attack"]["base"] = {"value": attack_value}
    if defense_mode == "dodge" and defense_value is not None:
        system["combat"]["dodge"]["base"] = {"value": defense_value}
    elif defense_mode == "block" and defense_value is not None:
        system["combat"]["block"]["base"] = {"value": defense_value}
    system["combat"]["wearArmor"]["base"] = {"value": wear_armor}

    act_value = record.get("act")
    if act_value is not None:
        system["ui"]["tabVisibility"]["mystic"]["value"] = True
        system["mystic"]["act"]["main"]["base"]["value"] = act_value

    zeon_value = record.get("zeon")
    if zeon_value is not None:
        system["ui"]["tabVisibility"]["mystic"]["value"] = True
        system["mystic"]["zeon"]["value"] = zeon_value
        system["mystic"]["zeon"]["max"] = zeon_value

    magic_projection = record.get("magic_projection")
    if magic_projection is not None:
        system["ui"]["tabVisibility"]["mystic"]["value"] = True
        system["mystic"]["magicProjection"]["base"]["value"] = magic_projection
        system["mystic"]["magicProjection"]["imbalance"]["offensive"]["base"]["value"] = magic_projection
        system["mystic"]["magicProjection"]["imbalance"]["defensive"]["base"]["value"] = magic_projection

    for field_key, system_key in (
        ("summon", "summon"),
        ("control", "control"),
        ("bind", "bind"),
        ("banish", "banish"),
    ):
        if record.get(field_key) is not None:
            system["ui"]["tabVisibility"]["mystic"]["value"] = True
            system["mystic"]["summoning"][system_key]["base"]["value"] = record[field_key]

    for sphere_key, sphere_value in infer_sphere_levels(record.get("magic_level_raw")).items():
        system["ui"]["tabVisibility"]["mystic"]["value"] = True
        system["mystic"]["magicLevel"]["spheres"][sphere_key]["value"] = sphere_value

    psychic_potential = record.get("psychic_potential")
    if psychic_potential is not None:
        system["ui"]["tabVisibility"]["psychic"]["value"] = True
        system["psychic"]["psychicPotential"]["base"]["value"] = psychic_potential

    psychic_projection = record.get("psychic_projection")
    if psychic_projection is not None:
        system["ui"]["tabVisibility"]["psychic"]["value"] = True
        system["psychic"]["psychicProjection"]["base"]["value"] = psychic_projection
        system["psychic"]["psychicProjection"]["imbalance"]["offensive"]["base"]["value"] = psychic_projection
        system["psychic"]["psychicProjection"]["imbalance"]["defensive"]["base"]["value"] = psychic_projection

    psychic_points = record.get("cv")
    if psychic_points is not None:
        system["ui"]["tabVisibility"]["psychic"]["value"] = True
        system["psychic"]["psychicPoints"]["value"] = psychic_points
        system["psychic"]["psychicPoints"]["max"] = psychic_points

    innate_psychic = record.get("innate")
    if innate_psychic is not None:
        system["ui"]["tabVisibility"]["psychic"]["value"] = True
        system["psychic"]["innatePsychicPower"]["amount"]["value"] = innate_psychic

    if record.get("psychic_powers") or record.get("disciplines"):
        system["ui"]["tabVisibility"]["psychic"]["value"] = True

    domine_text = " ".join(
        value
        for value in [
            record.get("raw_chunk", ""),
            record.get("powers", ""),
            record.get("natural_abilities", ""),
            record.get("ki", ""),
            record.get("techniques", ""),
            record.get("martial_arts", ""),
        ]
        if value
    )
    if any(term in normalize_key(domine_text) for term in ("ki", "tecnicas", "ars magnus", "acumulaciones")):
        system["ui"]["tabVisibility"]["domine"]["value"] = True

    if record.get("invocations") or record.get("metamagic"):
        system["ui"]["tabVisibility"]["mystic"]["value"] = True

    apply_ui_flags(
        system,
        " ".join(
            value
            for value in [
                record.get("natural_abilities", ""),
                record.get("essentials", ""),
                record.get("powers", ""),
                record.get("disciplines", ""),
                record.get("advantages", ""),
            ]
            if value
        ),
    )

    items = []
    armor_item = build_armor_item(record["name"], record.get("ta_raw"))
    if armor_item:
        items.append(armor_item)

    prepared_items = []
    for index, item in enumerate(items):
        item_id = stable_id(actor_id, item["type"], item["name"], str(index))
        prepared_item = copy.deepcopy(item)
        prepared_item["_id"] = item_id
        prepared_item.setdefault("folder", None)
        prepared_item.setdefault("sort", index * 10)
        prepared_item.setdefault("flags", {})
        prepared_item.setdefault("ownership", {"default": 0})
        prepared_item["_stats"] = build_stats_block()
        prepared_item["_key"] = f"!actors.items!{actor_id}.{item_id}"
        prepared_items.append(prepared_item)

    return {
        "_id": actor_id,
        "name": record["name"],
        "type": "character",
        "img": "icons/svg/mystery-man.svg",
        "prototypeToken": {
            "name": record["name"]
        },
        "items": prepared_items,
        "effects": [],
        "folder": None,
        "sort": 0,
        "flags": {
            MODULE_ID: {
                "sourceBook": record["source_book"],
                "sourceHeading": record["source_heading"],
                "page": record.get("page"),
                "variant": record.get("variant"),
                "rawClass": record.get("creature_class"),
                "rawDamage": record.get("damage_raw"),
                "rawTA": record.get("ta_raw"),
                "warnings": record.get("warnings", []),
            }
        },
        "system": system,
        "_stats": build_stats_block(),
        "ownership": {
            "default": 0
        },
        "_key": f"!actors!{actor_id}",
    }


def make_record(
    book_id: str,
    section_title: str,
    section_body: str,
    chunk: str,
    start_pos: int,
    profile_index: int,
) -> dict:
    page = extract_page(section_body, start_pos)
    variant = extract_variant(section_title, section_body, start_pos)
    fields = extract_labeled_fields(chunk)

    warnings: list[str] = []
    level, creature_class, gnosis = split_level_and_class(fields.get("level", ""))
    if fields.get("class"):
        creature_class = fields.get("class")
    life_points_raw = fields.get("points")
    life_points = parse_all_ints(life_points_raw)[0] if parse_all_ints(life_points_raw) else None

    if level is None:
        warnings.append("nivel_no_detectado")
    if life_points is None:
        warnings.append("vida_no_detectada")

    primary_stats = parse_primary_stats(fields)
    resistances = parse_resistances(fields)
    if not primary_stats:
        warnings.append("atributos_no_detectados")
    if not resistances:
        warnings.append("resistencias_no_detectadas")

    attack_raw = fields.get("attack")
    defense_raw = fields.get("defense")
    damage_raw = fields.get("damage")
    secondary_raw, secondary_skills, narrative = parse_secondary_skills(fields.get("secondary_skills"))

    record = {
        "id": f"{book_id}:{slugify(section_title)}:{profile_index}",
        "name": section_title if not variant else f"{section_title} ({variant})",
        "variant": variant,
        "source_book": BOOKS[book_id]["source_book"],
        "source_heading": section_title,
        "page": page,
        "profile_index": profile_index,
        "level": level,
        "creature_class": creature_class,
        "gnosis": gnosis,
        "life_points_raw": life_points_raw,
        "life_points": life_points,
        "category": fields.get("category"),
        "race": fields.get("race"),
        "primary_stats": primary_stats,
        "resistances": resistances,
        "initiative_raw": fields.get("turn"),
        "initiative": parse_all_ints(fields.get("turn"))[0] if parse_all_ints(fields.get("turn")) else None,
        "attack_raw": attack_raw,
        "attack": max(parse_all_ints(attack_raw), default=None),
        "defense_raw": defense_raw,
        "defense": max(parse_all_ints(defense_raw), default=None),
        "defense_mode": infer_defense_mode(defense_raw),
        "damage_raw": damage_raw,
        "wear_armor_raw": fields.get("wear_armor"),
        "wear_armor": parse_int(fields.get("wear_armor")),
        "ta_raw": fields.get("ta"),
        "act_raw": fields.get("act"),
        "act": parse_all_ints(fields.get("act"))[0] if parse_all_ints(fields.get("act")) else None,
        "zeon_raw": fields.get("zeon"),
        "zeon": parse_all_ints(fields.get("zeon"))[0] if parse_all_ints(fields.get("zeon")) else None,
        "magic_projection_raw": fields.get("magic_projection"),
        "magic_projection": max(parse_all_ints(fields.get("magic_projection")), default=None),
        "magic_level_raw": fields.get("magic_level") or fields.get("act"),
        "summon_raw": fields.get("summon"),
        "summon": max(parse_all_ints(fields.get("summon")), default=None),
        "control_raw": fields.get("control"),
        "control": max(parse_all_ints(fields.get("control")), default=None),
        "bind_raw": fields.get("bind"),
        "bind": max(parse_all_ints(fields.get("bind")), default=None),
        "banish_raw": fields.get("banish"),
        "banish": max(parse_all_ints(fields.get("banish")), default=None),
        "psychic_potential_raw": fields.get("psychic_potential"),
        "psychic_potential": max(parse_all_ints(fields.get("psychic_potential")), default=None),
        "cv_raw": fields.get("cv"),
        "cv": max(parse_all_ints(fields.get("cv")), default=None),
        "disciplines": fields.get("disciplines"),
        "innate_raw": fields.get("innate"),
        "innate": max(parse_all_ints(fields.get("innate")), default=None),
        "psychic_projection_raw": fields.get("psychic_projection"),
        "psychic_projection": max(parse_all_ints(fields.get("psychic_projection")), default=None),
        "psychic_powers": fields.get("psychic_powers"),
        "natural_abilities": fields.get("natural_abilities"),
        "essentials": fields.get("essentials"),
        "powers": fields.get("powers"),
        "advantages": fields.get("advantages"),
        "ki": fields.get("ki"),
        "accumulations": fields.get("accumulations"),
        "techniques": fields.get("techniques"),
        "martial_arts": fields.get("martial_arts"),
        "invocations": fields.get("invocations"),
        "metamagic": fields.get("metamagic"),
        "elan": fields.get("elan"),
        "size_raw": fields.get("size"),
        "size_value": parse_all_ints(fields.get("size"))[0] if parse_all_ints(fields.get("size")) else None,
        "regeneration_raw": fields.get("regen"),
        "regeneration": max(parse_all_ints(fields.get("regen")), default=0),
        "movement_raw": fields.get("movement"),
        "movement": parse_all_ints(fields.get("movement"))[0] if parse_all_ints(fields.get("movement")) else 0,
        "fatigue_raw": fields.get("fatigue"),
        "fatigue": max(parse_all_ints(fields.get("fatigue")), default=0),
        "secondary_skills_raw": secondary_raw,
        "secondary_skills": secondary_skills,
        "narrative": narrative,
        "raw_chunk": chunk,
        "warnings": warnings,
    }
    apply_record_override(book_id, record)
    return record


def apply_record_override(book_id: str, record: dict) -> None:
    override_key = (
        book_id,
        record["source_heading"],
        record.get("level"),
        record.get("page"),
        record.get("profile_index"),
    )
    override = RECORD_OVERRIDES.get(override_key)
    if not override:
        return

    record.update(override)
    if record.get("variant"):
        record["name"] = f"{record['source_heading']} ({record['variant']})"
    else:
        record["name"] = record["source_heading"]


def dedupe_names(records: list[dict]) -> None:
    seen: dict[str, int] = {}
    for record in records:
        base_name = record["name"]
        if base_name not in seen:
            seen[base_name] = 1
            continue

        seen[base_name] += 1
        record["name"] = f"{base_name} ({seen[base_name]})"


def extract_records_from_flat_text(book_id: str, source_text: str) -> list[dict]:
    config = BOOKS[book_id]
    page_title_overrides = config.get("page_title_overrides", {})
    sequential_title_overrides = config.get("sequential_title_overrides", [])
    page_hits: dict[int, int] = {}
    matches = list(LEVEL_MARKER_RE.finditer(source_text))
    records = []

    for profile_index, match in enumerate(matches, start=1):
        start = match.start()
        end = matches[profile_index].start() if profile_index < len(matches) else len(source_text)
        chunk = source_text[start:end].strip()
        if not POINTS_MARKER_RE.search(chunk):
            continue

        page = extract_page(source_text, start)
        section_title = None
        consumed_page_override = False
        if page in page_title_overrides:
            page_index = page_hits.get(page, 0)
            titles = page_title_overrides[page]
            if page_index < len(titles):
                section_title = titles[page_index]
                consumed_page_override = True
        if not section_title:
            section_title = extract_flat_title(source_text, start)
        if not section_title:
            continue

        record = make_record(
            book_id,
            section_title,
            source_text,
            chunk,
            start,
            profile_index,
        )
        record["variant"] = None
        record["name"] = record["source_heading"]

        if not is_viable_record(record):
            continue
        if len(records) < len(sequential_title_overrides):
            record["source_heading"] = sequential_title_overrides[len(records)]
            record["variant"] = None
            record["name"] = record["source_heading"]
        if consumed_page_override and page is not None:
            page_hits[page] = page_hits.get(page, 0) + 1
        records.append(record)

    dedupe_names(records)
    return records


def extract_records(book_id: str, source_text: str) -> list[dict]:
    config = BOOKS[book_id]
    scoped_text = slice_section(source_text, config["start_marker"], config["end_marker"])
    if config.get("mode") == "flat":
        return extract_records_from_flat_text(book_id, scoped_text)

    records = []

    for section in iter_sections(scoped_text):
        if not LEVEL_MARKER_RE.search(section["body"]):
            continue

        for profile_index, (start, end) in enumerate(find_profile_windows(section["body"]), start=1):
            chunk = section["body"][start:end].strip()
            if not POINTS_MARKER_RE.search(chunk):
                continue
            record = make_record(
                book_id,
                section["title"],
                section["body"],
                chunk,
                start,
                profile_index,
            )
            if not is_viable_record(record):
                continue
            records.append(record)

    dedupe_names(records)
    return records


def build_dataset(book_id: str, records: list[dict], template: dict) -> tuple[dict, dict]:
    config = BOOKS[book_id]
    documents = [build_actor_document(record, template) for record in records]
    serializable_records = []
    for record in records:
        serializable = copy.deepcopy(record)
        serializable["secondary_skills"] = {
            ".".join(path): value
            for path, value in record.get("secondary_skills", {}).items()
        }
        serializable_records.append(serializable)

    dataset = {
        "id": book_id,
        "label": config["label"],
        "sourceBook": config["source_book"],
        "compendiumLabel": config["compendium_label"],
        "packPath": f"packs/{book_id}",
        "count": len(documents),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "documents": documents,
    }

    debug_records = {
        "id": book_id,
        "label": config["label"],
        "sourceBook": config["source_book"],
        "count": len(records),
        "generatedAt": dataset["generatedAt"],
        "records": serializable_records,
        "warningCount": sum(len(record["warnings"]) for record in records),
    }

    return dataset, debug_records


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera datasets de bestiario para Animu Exxet.")
    parser.add_argument("--core", help="Ruta al markdown de Core Exxet")
    parser.add_argument(
        "--walking",
        help="Ruta al markdown de Los que caminaron con nosotros",
    )
    parser.add_argument(
        "--output-dir",
        default=str(OUTPUT_DIR),
        help="Directorio de salida para los JSON generados",
    )
    args = parser.parse_args()

    template = read_json(TEMPLATE_PATH)
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    PACKS_DIR.mkdir(parents=True, exist_ok=True)

    overrides = {
        "core-exxet": args.core,
        "caminaron-con-nosotros": args.walking,
    }
    source_paths = {
        book_id: discover_path(overrides.get(book_id), config["default_candidates"])
        for book_id, config in BOOKS.items()
    }

    dataset_index = {
        "moduleId": MODULE_ID,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "datasets": [],
    }

    for book_id, source_path in source_paths.items():
        source_text = source_path.read_text(encoding="utf-8")
        records = extract_records(book_id, source_text)
        dataset, debug_records = build_dataset(book_id, records, template)

        write_json(output_dir / BOOKS[book_id]["filename"], dataset)
        write_json(output_dir / BOOKS[book_id]["records_filename"], debug_records)
        write_pack_source(book_id, dataset["documents"])

        dataset_index["datasets"].append(
            {
                "id": book_id,
                "label": dataset["label"],
                "sourceBook": dataset["sourceBook"],
                "filename": BOOKS[book_id]["filename"],
                "recordsFilename": BOOKS[book_id]["records_filename"],
                "packPath": dataset["packPath"],
                "count": dataset["count"],
                "sourcePath": str(source_path),
            }
        )

        print(f"{dataset['label']}: {dataset['count']} fichas generadas")

    write_json(output_dir / "index.json", dataset_index)
    print(f"Índice actualizado en {output_dir / 'index.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
