import re, json, hashlib, shutil
from pathlib import Path
import plyvel

COLUMNS_MD = Path("/animu/data/docs_md/Anima Beyond Fantasy - Prometheum exxet_columns.md")
PACKS_DIR = Path("/animu-exxet/packs")
OUTPUT_DIR = Path("/animu-exxet/data/generated")
PACK_ID = "artifacts-exxet"
PACK_LABEL = "Artifacts Exxet"

PAGE_RE = re.compile(r"_Página\s+(\d+)_")
NIVEL_RE = re.compile(r"^Nivel de Poder:\s*(.+)$", re.MULTILINE)
FABULA_RE = re.compile(r"^Fábula:\s*(.+)$", re.MULTILINE)
WEAPON_RE = re.compile(r"Daño\nTurno\nFUE R\.", re.IGNORECASE)
ARMOR_RE = re.compile(r"Requ\.?\s*de\s*\nArmadura", re.IGNORECASE)
NUMBER_RE = re.compile(r"-?\d+")
CRITIC_MAP = {"fil":"cut","con":"impact","pen":"thrust","cal":"heat","ele":"electricity","fri":"cold","ene":"energy"}


# Names that are clearly wrong - skip these entries
SKIP_NAMES = {
    "0 8 2",
    "Apolyon Es Un Ente Consciente, Capaz de",
    "Con la Desaparición de Thanos, el Legislador",
    "En Estos Momentos, Hace Más de Trescientos",
    "En Estos Momentos Dos de las Armaduras Están",
    "Necrom Se Volvió Infamemente Conocida Durante la",
    "Naturalmente, Espera Con Ansia A Alguien Que la",
    "El Arma Tiene al Menos Unos Dos",
    "Pese A Que, Igual Que las Otras, el Arma Fue",
    "Ondinias Es Visualmente Fascinante Por Su",
}

# Force certain items to be notes instead of weapons/armors
FORCE_NOTE = {"Onydas", "Redes Mantincore", "Ondinias"}

def sid(*p, l=16): return hashlib.sha1("::".join(p).encode()).hexdigest()[:l]
def pi(s):
    m = NUMBER_RE.search(re.sub(r"\s+","",str(s or "")))
    return int(m.group(0)) if m else 0
def st():
    return {"systemId":"animabf","systemVersion":"2.2.1","coreVersion":"14.359",
            "createdTime":1713571200000,"modifiedTime":1713571200000,"lastModifiedBy":"animuExxetGen001"}
def smart_title(t):
    sw = {"de","del","la","el","los","las","y","o","en","al"}
    return " ".join(w.capitalize() if i==0 or w.lower() not in sw else w.lower() for i,w in enumerate(t.strip().split()))

def find_title(text, pos):
    window = text[max(0,pos-3000):pos]
    lines = window.split("\n")
    fab = None
    for j in range(len(lines)-1,-1,-1):
        if lines[j].strip().startswith("Fábula"):
            fab = j; break
    if fab is None: return None
    for j in range(fab-1, max(fab-40,-1), -1):
        line = lines[j].strip()
        if not line: continue
        if line.startswith("---") or line.startswith("_Página"):
            for k in range(j+1, fab):
                c = lines[k].strip()
                if c and not c.startswith("_") and not c.startswith("---"):
                    return c
            break
        prev = lines[j-1].strip() if j>0 else ""
        if len(line)<50 and (not prev or prev.startswith("---") or prev.startswith("_") or prev.endswith(".") or "Reglas" in prev or "Nivel de Poder" in prev):
            return line
    return None

def is_valid_name(n):
    if not n or len(n)>60: return False
    if n[0].islower(): return False
    if n.endswith(".") or n.endswith(","): return False
    if "Noción" in n or "Ritual" in n: return False
    return True

def parse_weapon(text_after):
    lines = [l.strip() for l in text_after.split("\n") if l.strip()]
    vals, crits = [], []
    for l in lines:
        if l.startswith("Tipo de arma"): break
        if NUMBER_RE.match(l.replace("+","").replace("-","").replace("/","").strip()): vals.append(l)
        elif l.lower() in CRITIC_MAP: crits.append(CRITIC_MAP[l.lower()])
    dmg = pi(vals[0]) if vals else 0
    turno = pi(vals[1]) if len(vals)>1 else 0
    fue = pi(vals[2]) if len(vals)>2 else 0
    c1 = crits[0] if crits else "-"
    c2 = crits[1] if len(crits)>1 else "-"
    tipo_s = text_after.split("Tipo de arma")[-1] if "Tipo de arma" in text_after else ""
    tn = [pi(l) for l in tipo_s.split("\n") if l.strip() and NUMBER_RE.match(l.strip().replace("-",""))][:3]
    ent = tn[0] if tn else 0
    rot = tn[1] if len(tn)>1 else 0
    pres = tn[2] if len(tn)>2 else 0
    wt = ""
    for l in tipo_s.split("\n"):
        l = l.strip()
        if l and not l.startswith("Especial") and not NUMBER_RE.match(l.replace("-","")) and l != "Reglas Especiales":
            wt = l; break
    rules = ""
    if "Reglas Especiales" in text_after:
        rl = []
        for l in text_after.split("Reglas Especiales")[-1].split("\n"):
            l = l.strip()
            if not l or l.startswith("---") or l.startswith("_Página"): break
            rl.append(l)
        rules = ", ".join(rl)
    return {"damage":dmg,"turno":turno,"fue_req":fue,"crit1":c1,"crit2":c2,"entereza":ent,"rotura":rot,"presencia":pres,"weapon_type":wt,"rules":rules}

def mk_weapon(name, wid, s):
    return {"_id":wid,"name":name,"type":"weapon","img":"icons/weapons/swords/greatsword-crossguard-steel.webp",
            "effects":[],"folder":None,"sort":0,"flags":{},"ownership":{"default":0},"_stats":st(),"_key":f"!items!{wid}",
            "system":{"special":{"value":f"Tipo: {s['weapon_type']}. {s['rules']}"[:500]},
                "integrity":{"base":{"value":s["entereza"]},"final":{"value":0},"special":{"value":0}},
                "breaking":{"base":{"value":s["rotura"]},"final":{"value":0},"special":{"value":0}},
                "attack":{"base":{"value":0},"final":{"value":0},"special":{"value":0}},
                "block":{"base":{"value":0},"final":{"value":0},"special":{"value":0}},
                "damage":{"base":{"value":s["damage"]},"final":{"value":0},"special":{"value":0}},
                "initiative":{"base":{"value":s["turno"]},"final":{"value":0},"special":{"value":0}},
                "presence":{"base":{"value":s["presencia"]},"final":{"value":0},"special":{"value":0}},
                "size":{"value":"medium"},
                "strRequired":{"oneHand":{"base":{"value":s["fue_req"]},"final":{"value":0}},"twoHands":{"base":{"value":0},"final":{"value":0}}},
                "quality":{"value":0},"oneOrTwoHanded":{"value":""},"knowledgeType":{"value":"known"},
                "manageabilityType":{"value":"one_hand"},"shotType":{"value":"throw"},"isRanged":{"value":False},
                "range":{"base":{"value":0},"final":{"value":0}},"cadence":{"value":""},
                "reload":{"base":{"value":0},"final":{"value":0}},"sizeProportion":{"value":"normal"},
                "weaponStrength":{"base":{"value":0},"final":{"value":0}},
                "critic":{"primary":{"value":s["crit1"]},"secondary":{"value":s["crit2"]}},
                "isShield":{"value":False},"equipped":{"value":True}}}

def mk_armor(name, aid):
    return {"_id":aid,"name":name,"type":"armor","img":"icons/equipment/chest/breastplate-cuirass-steel-grey.webp",
            "effects":[],"folder":None,"sort":0,"flags":{},"ownership":{"default":0},"_stats":st(),"_key":f"!items!{aid}",
            "system":{**{k:{"base":{"value":0},"final":{"value":0},"value":0} for k in ("cut","pierce","impact","thrust","heat","electricity","cold","energy")},
                "integrity":{"base":{"value":0},"final":{"value":0}},"presence":{"base":{"value":0},"final":{"value":0}},
                "movementRestriction":{"base":{"value":0},"final":{"value":0}},"naturalPenalty":{"base":{"value":0},"final":{"value":0}},
                "wearArmorRequirement":{"base":{"value":0},"final":{"value":0}},"isEnchanted":{"value":True},
                "type":{"value":"hard"},"localization":{"value":"complete"},"quality":{"value":0},"equipped":{"value":True}}}

def mk_note(name, nid):
    return {"_id":nid,"name":name,"type":"note","img":"icons/sundries/scrolls/scroll-runed-brown-purple.webp",
            "effects":[],"folder":None,"sort":0,"flags":{},"ownership":{"default":0},"_stats":st(),"_key":f"!items!{nid}","system":{}}

text = COLUMNS_MD.read_text(encoding="utf-8")
items = []
seen = set()

def uname(n):
    if not n: n = "Artefacto"
    n = smart_title(n)
    if n in seen:
        i = 2
        while f"{n} ({i})" in seen: i += 1
        n = f"{n} ({i})"
    seen.add(n)
    return n

# Process each Nivel de Poder block
for m in NIVEL_RE.finditer(text):
    title = find_title(text, m.start())
    if not is_valid_name(title):
        continue
    
    page_m = PAGE_RE.search(text[max(0,m.start()-500):m.start()])
    page = int(page_m.group(1)) if page_m else None
    
    # Check for weapon/armor tables after this Nivel de Poder
    after_start = m.end()
    next_nivel = NIVEL_RE.search(text, after_start)
    after_end = next_nivel.start() if next_nivel else len(text)
    after_text = text[after_start:after_end]
    
    weapon_tables = list(WEAPON_RE.finditer(after_text))
    armor_tables = list(ARMOR_RE.finditer(after_text))
    
    if title in SKIP_NAMES or any(s.lower() in title.lower() for s in SKIP_NAMES) or (title and title[0].isdigit()):
        continue
    name = uname(title)
    
    if title in FORCE_NOTE:
        nid = sid(PACK_ID, "n", name)
        items.append(("note", mk_note(name, nid), page))
        continue

    if weapon_tables:
        for wi, wm in enumerate(weapon_tables):
            suffix = f" ({wi+1})" if len(weapon_tables) > 1 else ""
            wname = f"{name}{suffix}" if not suffix else uname(f"{title}")
            wid = sid(PACK_ID, "w", wname)
            block_end = min(
                weapon_tables[wi+1].start() if wi+1 < len(weapon_tables) else len(after_text),
                armor_tables[0].start() if armor_tables else len(after_text),
                after_text.find("\n---\n") if "\n---\n" in after_text else len(after_text)
            )
            stats = parse_weapon(after_text[wm.end():block_end])
            items.append(("weapon", mk_weapon(wname, wid, stats), page))
        # Companion note
        nid = sid(PACK_ID, "wn", name)
        items.append(("note", mk_note(f"{name} (nota)", nid), page))
    elif armor_tables:
        aid = sid(PACK_ID, "a", name)
        items.append(("armor", mk_armor(name, aid), page))
        nid = sid(PACK_ID, "an", name)
        items.append(("note", mk_note(f"{name} (nota)", nid), page))
    else:
        nid = sid(PACK_ID, "n", name)
        items.append(("note", mk_note(name, nid), page))

w = sum(1 for t,_,_ in items if t=="weapon")
a = sum(1 for t,_,_ in items if t=="armor")
n = sum(1 for t,_,_ in items if t=="note")
print(f"Total: {len(items)} ({w} armas, {a} armaduras, {n} notas)")

# Build LevelDB
ldb = PACKS_DIR / PACK_ID
if ldb.exists(): shutil.rmtree(ldb)
ldb.mkdir(parents=True)
db = plyvel.DB(str(ldb), create_if_missing=True)
sb = st()

rid = sid("folder",PACK_ID,"root")
db.put(f"!folders!{rid}".encode(), json.dumps({"color":"#000000","name":PACK_LABEL,"sorting":"a","type":"Item","folder":None,"_id":rid,"sort":0,"flags":{},"_stats":sb,"_key":f"!folders!{rid}"},ensure_ascii=False).encode())

cf = {}
for idx,(k,l) in enumerate([("weapon","Armas"),("armor","Armaduras"),("note","Artefactos y Notas")]):
    fid = sid("folder",PACK_ID,k)
    db.put(f"!folders!{fid}".encode(), json.dumps({"color":"#000000","name":l,"sorting":"a","type":"Item","folder":rid,"_id":fid,"sort":(idx+1)*10,"flags":{},"_stats":sb,"_key":f"!folders!{fid}"},ensure_ascii=False).encode())
    cf[k] = fid

for si,(t,item,p) in enumerate(items):
    item["folder"] = cf[t]
    item["sort"] = si*10
    db.put(item["_key"].encode(), json.dumps(item,ensure_ascii=False).encode())

db.close()
print(f"LevelDB en {ldb}")

idx_data = [{"name":i["name"],"type":t,"page":p} for t,i,p in items]
(OUTPUT_DIR/"artifacts-exxet.index.json").write_text(json.dumps(idx_data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
