const MODULE_ID = 'animu-exxet';

// Cell positions in the "Resumen" sheet (standard Anima Excel)
const CELLS = {
  name: 'M3', level: 'F11', class: 'L11', lifePoints: 'E12', category: 'L12',
  strength: 'F13', dexterity: 'J13', agility: 'N13', constitution: 'R13',
  power: 'F14', intelligence: 'J14', willpower: 'N14', perception: 'R14',
  presence: 'H15',
  rf: 'F16', rm: 'J16', rp: 'N16', rv: 'R16', re: 'V16',
  initiative: 'H19', attack: 'H22', defense: 'H25', damage: 'H28',
  taLabel: 'H31',
  taFil: 'H32', taCon: 'L32', taPen: 'P32', taCal: 'T32',
  taEle: 'H33', taFri: 'L33', taEne: 'P33',
  zeon: 'V48', act: 'F50', magicProjection: 'J48',
  summon: 'S50', control: 'X50', bind: 'S51', banish: 'X51',
  cv: 'H60', innate: 'O60',
  psychicPotential: 'J62', psychicProjection: 'K64',
  fatigue: 'H95', size: 'G93', movement: 'S93',
  secondarySkills: 'D98',
  advantages: 'K73', naturalAbilities: 'K76', special: 'G79',
  essentialAbilities: 'K84', powers: 'K87',
  kiSkills: 'H39', techniques: 'H43',
  magicLevel: 'G52',
  psychicDisciplines: 'H66', psychicPowers: 'H69',
};

const SECONDARY_MAP = {
  'acrobacias': ['secondaries', 'athletics', 'acrobatics'],
  'atletismo': ['secondaries', 'athletics', 'athleticism'],
  'montar': ['secondaries', 'athletics', 'ride'],
  'nadar': ['secondaries', 'athletics', 'swim'],
  'trepar': ['secondaries', 'athletics', 'climb'],
  'saltar': ['secondaries', 'athletics', 'jump'],
  'pilotar': ['secondaries', 'athletics', 'piloting'],
  'frialdad': ['secondaries', 'vigor', 'composure'],
  'proezas de fuerza': ['secondaries', 'vigor', 'featsOfStrength'],
  'res. dolor': ['secondaries', 'vigor', 'withstandPain'],
  'resistir el dolor': ['secondaries', 'vigor', 'withstandPain'],
  'advertir': ['secondaries', 'perception', 'notice'],
  'buscar': ['secondaries', 'perception', 'search'],
  'rastrear': ['secondaries', 'perception', 'track'],
  'animales': ['secondaries', 'intellectual', 'animals'],
  'ciencia': ['secondaries', 'intellectual', 'science'],
  'ley': ['secondaries', 'intellectual', 'law'],
  'herbolaria': ['secondaries', 'intellectual', 'herbalLore'],
  'historia': ['secondaries', 'intellectual', 'history'],
  'tactica': ['secondaries', 'intellectual', 'tactics'],
  'medicina': ['secondaries', 'intellectual', 'medicine'],
  'memorizar': ['secondaries', 'intellectual', 'memorize'],
  'navegacion': ['secondaries', 'intellectual', 'navigation'],
  'ocultismo': ['secondaries', 'intellectual', 'occult'],
  'tasacion': ['secondaries', 'intellectual', 'appraisal'],
  'v. magica': ['secondaries', 'intellectual', 'magicAppraisal'],
  'valoracion magica': ['secondaries', 'intellectual', 'magicAppraisal'],
  'estilo': ['secondaries', 'social', 'style'],
  'intimidar': ['secondaries', 'social', 'intimidate'],
  'liderazgo': ['secondaries', 'social', 'leadership'],
  'persuasion': ['secondaries', 'social', 'persuasion'],
  'comercio': ['secondaries', 'social', 'trading'],
  'callejeo': ['secondaries', 'social', 'streetwise'],
  'etiqueta': ['secondaries', 'social', 'etiquette'],
  'cerrajeria': ['secondaries', 'subterfuge', 'lockPicking'],
  'disfraz': ['secondaries', 'subterfuge', 'disguise'],
  'ocultarse': ['secondaries', 'subterfuge', 'hide'],
  'robo': ['secondaries', 'subterfuge', 'theft'],
  'sigilo': ['secondaries', 'subterfuge', 'stealth'],
  'tramperia': ['secondaries', 'subterfuge', 'trapLore'],
  'venenos': ['secondaries', 'subterfuge', 'poisons'],
  'arte': ['secondaries', 'creative', 'art'],
  'baile': ['secondaries', 'creative', 'dance'],
  'forja': ['secondaries', 'creative', 'forging'],
  'runas': ['secondaries', 'creative', 'runes'],
  'alquimia': ['secondaries', 'creative', 'alchemy'],
  'animismo': ['secondaries', 'creative', 'animism'],
  'musica': ['secondaries', 'creative', 'music'],
  'trucos de manos': ['secondaries', 'creative', 'sleightOfHand'],
  'orfebreria': ['secondaries', 'creative', 'jewelry'],
  'confeccion': ['secondaries', 'creative', 'tailoring'],
};

function safeInt(v) {
  if (v == null) return 0;
  if (typeof v === 'number') return Math.floor(v);
  const m = String(v).replace(/\s/g, '').match(/-?\d+/);
  return m ? parseInt(m[0]) : 0;
}

function safeStr(v) {
  return v == null ? '' : String(v).trim();
}

function cellValue(sheet, ref) {
  const cell = sheet[ref];
  return cell ? cell.v : null;
}

function normalizeSkillName(name) {
  return name.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
    .replace(/\([^)]*\)/g, '').trim();
}

function parseSecondarySkills(raw) {
  const skills = {};
  if (!raw) return skills;
  for (const part of String(raw).split(',')) {
    const m = part.trim().match(/(.+?)\s+(-?\d+)\s*$/);
    if (!m) continue;
    const name = normalizeSkillName(m[1]);
    const value = parseInt(m[2]);
    const path = SECONDARY_MAP[name];
    if (path) skills[path.join('.')] = value;
  }
  return skills;
}

function calcMod(value) {
  if (value <= 0) return 0;
  if (value < 4) return value * 10 - 40;
  return Math.min(
    (Math.floor((value + 5) / 5) + Math.floor((value + 4) / 5) + Math.floor((value + 2) / 5) - 4) * 5,
    45
  );
}

export function parseExcelToActorData(workbook, fileName) {
  // Try Resumen first (universal), fall back to NamedRangesList
  const sheet = workbook.Sheets['Resumen'];
  if (!sheet) throw new Error(`No "Resumen" sheet in ${fileName}`);

  const get = ref => cellValue(sheet, ref);
  const getInt = ref => safeInt(get(ref));
  const getStr = ref => safeStr(get(ref));

  const name = getStr(CELLS.name) || fileName.replace(/\.xlsm?$/i, '');
  const level = getInt(CELLS.level);
  const presenceBase = getInt(CELLS.presence) || (level <= 0 ? 20 : 25 + level * 5);

  const primaries = {
    agility: getInt(CELLS.agility),
    constitution: getInt(CELLS.constitution),
    dexterity: getInt(CELLS.dexterity),
    strength: getInt(CELLS.strength),
    intelligence: getInt(CELLS.intelligence),
    perception: getInt(CELLS.perception),
    power: getInt(CELLS.power),
    willPower: getInt(CELLS.willpower),
  };

  const defenseRaw = getStr(CELLS.defense);
  const isBlock = defenseRaw.toLowerCase().includes('parada');

  const skills = parseSecondarySkills(getStr(CELLS.secondarySkills));

  // Build the actor data matching animabf structure
  const system = {};

  // We'll let Foundry/animabf fill the template, just set the values we have
  return {
    name,
    type: 'character',
    img: 'icons/svg/mystery-man.svg',
    system: {
      version: 1,
      ui: {
        contractibleItems: {},
        tabVisibility: {
          mystic: { value: !!(getInt(CELLS.zeon) || getInt(CELLS.act) || getInt(CELLS.magicProjection)) },
          domine: { value: !!(getStr(CELLS.kiSkills) || getStr(CELLS.techniques)) },
          psychic: { value: !!(getInt(CELLS.psychicPotential) || getInt(CELLS.cv)) },
        }
      },
      general: {
        settings: { openRolls: { value: 90 }, fumbles: { value: 3 }, openOnDoubles: { value: false }, defenseType: { value: '' } },
        modifiers: { physicalActions: { value: 0 }, allActions: { base: { value: 0 }, final: { value: 0 } }, naturalPenalty: { byArmors: { value: 0 }, byWearArmorRequirement: { value: 0 } }, extraDamage: { value: 0 } },
        destinyPoints: { base: { value: 0 }, final: { value: 0 } },
        presence: { value: 0, base: { value: presenceBase } },
        aspect: { hair: { value: '' }, eyes: { value: '' }, height: { value: '' }, weight: { value: '' }, age: { value: '' }, gender: { value: '' }, race: { value: getStr(CELLS.class) }, ethnicity: { value: '' }, appearance: { value: '' }, size: { value: String(getInt(CELLS.size)) } },
        advantages: [], contacts: [], inventory: [],
        money: { cooper: { value: 0 }, silver: { value: 0 }, gold: { value: 0 } },
        description: { value: `<p>Importado desde ${fileName}</p>`, enriched: '' },
        disadvantages: [], elan: [],
        experience: { current: { value: 0 }, next: { value: 0 } },
        languages: { base: { value: '' }, others: [] },
        levels: [{ _id: foundry.utils.randomID(), type: 'level', name, flags: { version: 1 }, system: { level } }],
        notes: [],
        titles: [],
      },
      characteristics: {
        primaries: Object.fromEntries(
          Object.entries(primaries).map(([k, v]) => [k, { value: v, mod: calcMod(v) }])
        ),
        secondaries: {
          lifePoints: { value: getInt(CELLS.lifePoints), max: getInt(CELLS.lifePoints) },
          initiative: { base: { value: getInt(CELLS.initiative) }, final: { value: 0 } },
          fatigue: { value: getInt(CELLS.fatigue), max: getInt(CELLS.fatigue) },
          regenerationType: { mod: { value: 0 }, final: { value: 0 } },
          regeneration: { normal: { value: 0, period: '' }, resting: { value: 0, period: '' }, recovery: { value: 0, period: '' } },
          movementType: { mod: { value: getInt(CELLS.movement) - primaries.agility }, final: { value: 0 } },
          movement: { maximum: { value: 0 }, running: { value: 0 } },
          resistances: {
            physical: { base: { value: getInt(CELLS.rf) }, final: { value: 0 } },
            disease: { base: { value: getInt(CELLS.rv) }, final: { value: 0 } },
            poison: { base: { value: getInt(CELLS.re) }, final: { value: 0 } },
            magic: { base: { value: getInt(CELLS.rm) }, final: { value: 0 } },
            psychic: { base: { value: getInt(CELLS.rp) }, final: { value: 0 } },
          }
        }
      },
      secondaries: Object.fromEntries(
        ['athletics', 'vigor', 'perception', 'intellectual', 'social', 'subterfuge', 'creative'].map(group => {
          const groupSkills = Object.entries(SECONDARY_MAP).filter(([, path]) => path[1] === group);
          return [group, Object.fromEntries(
            groupSkills.map(([, path]) => {
              const key = path.join('.');
              return [path[2], { base: { value: skills[key] || 0 }, final: { value: 0 } }];
            })
          )];
        }).concat([['secondarySpecialSkills', []]])
      ),
      combat: {
        attack: { base: { value: getInt(CELLS.attack) }, final: { value: 0 } },
        block: { base: { value: isBlock ? getInt(CELLS.defense) : 0 }, final: { value: 0 } },
        dodge: { base: { value: isBlock ? 0 : getInt(CELLS.defense) }, final: { value: 0 } },
        wearArmor: { value: 0 },
        totalArmor: { at: Object.fromEntries(['cut', 'impact', 'thrust', 'heat', 'electricity', 'cold', 'energy'].map(k => [k, { value: 0 }])) },
        combatSpecialSkills: [], combatTables: [], ammo: [], weapons: [], armors: [],
      },
      mystic: {
        act: { main: { base: { value: getInt(CELLS.act) }, final: { value: 0 } }, alternative: { base: { value: 0 }, final: { value: 0 } } },
        zeon: { accumulated: { value: null }, value: getInt(CELLS.zeon), max: getInt(CELLS.zeon) },
        zeonRegeneration: { base: { value: 0 }, final: { value: 0 } },
        innateMagic: { main: { value: 0 }, alternative: { value: 0 } },
        magicProjection: { base: { value: getInt(CELLS.magicProjection) }, final: { value: 0 }, imbalance: { offensive: { base: { value: 0 }, final: { value: 0 } }, defensive: { base: { value: 0 }, final: { value: 0 } } } },
        magicLevel: { spheres: Object.fromEntries(['essence', 'water', 'earth', 'creation', 'darkness', 'necromancy', 'light', 'destruction', 'air', 'fire', 'illusion'].map(k => [k, { value: 0 }])), total: { value: 0 }, used: { value: 0 } },
        summoning: {
          summon: { base: { value: getInt(CELLS.summon) }, final: { value: 0 } },
          banish: { base: { value: getInt(CELLS.banish) }, final: { value: 0 } },
          bind: { base: { value: getInt(CELLS.bind) }, final: { value: 0 } },
          control: { base: { value: getInt(CELLS.control) }, final: { value: 0 } },
        },
        spells: [], spellMaintenances: [], selectedSpells: [], summons: [], metamagics: [],
      },
      domine: {
        kiSkills: [], nemesisSkills: [], arsMagnus: [], martialArts: [], creatures: [], specialSkills: [], techniques: [],
        seals: { minor: Object.fromEntries(['earth', 'metal', 'wind', 'water', 'wood'].map(k => [k, { isActive: { value: false } }])), major: Object.fromEntries(['earth', 'metal', 'wind', 'water', 'wood'].map(k => [k, { isActive: { value: false } }])) },
        martialKnowledge: { used: { value: 0 }, max: { value: 0 } },
        kiAccumulation: Object.fromEntries(['strength', 'agility', 'dexterity', 'constitution', 'willPower', 'power'].map(k => [k, { accumulated: { value: 0 }, base: { value: 0 }, final: { value: 0 } }]).concat([['generic', { value: 0, max: 0 }]])),
      },
      psychic: {
        psychicPotential: { base: { value: getInt(CELLS.psychicPotential) }, final: { value: 0 } },
        psychicProjection: { base: { value: getInt(CELLS.psychicProjection) }, final: { value: 0 }, imbalance: { offensive: { base: { value: 0 }, final: { value: 0 } }, defensive: { base: { value: 0 }, final: { value: 0 } } } },
        psychicPoints: { value: getInt(CELLS.cv), max: getInt(CELLS.cv) },
        psychicPowers: [], psychicDisciplines: [], mentalPatterns: [],
        innatePsychicPower: { amount: { value: getInt(CELLS.innate) } },
        innatePsychicPowers: [],
      },
    },
    prototypeToken: {
      name, displayName: 0, actorLink: false, width: 1, height: 1,
      lockRotation: false, rotation: 0, alpha: 1, disposition: 1, displayBars: 0,
      bar1: { attribute: 'characteristics.secondaries.lifePoints' },
      bar2: { attribute: null },
      flags: { levels: { tokenHeight: 0 } },
      randomImg: false,
      light: { dim: 0, bright: 0, angle: 360, color: null, alpha: 0.25, animation: { speed: 5, intensity: 5, type: null, reverse: false }, coloration: 1, attenuation: 0.5, luminosity: 0.5, saturation: 0, contrast: 0, shadows: 0, darkness: { min: 0, max: 1 } },
      texture: { src: 'icons/svg/mystery-man.svg', tint: null, scaleX: 1, scaleY: 1, offsetX: 0, offsetY: 0, rotation: 0 },
      sight: { angle: 360, enabled: primaries.perception > 0, range: primaries.perception * 20, brightness: 1, visionMode: 'basic', attenuation: 0.1, saturation: 0, contrast: 0 },
      appendNumber: false, prependAdjective: false, detectionModes: [],
    },
    items: [],
    effects: [],
  };
}

export async function importExcelFiles(files, targetFolder) {
  if (typeof XLSX === 'undefined') {
    ui.notifications.error('La librer\u00eda XLSX no est\u00e1 cargada.');
    return 0;
  }

  let imported = 0;
  const errors = [];

  for (const file of files) {
    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: 'array' });
      const actorData = parseExcelToActorData(workbook, file.name);
      actorData.folder = targetFolder?.id ?? null;
      await Actor.create(actorData);
      imported++;
      ui.notifications.info(`${file.name}: ${actorData.name} importado`);
    } catch (e) {
      console.error(`${MODULE_ID} | Error importing ${file.name}:`, e);
      errors.push(`${file.name}: ${e.message}`);
    }
  }

  if (errors.length) {
    ui.notifications.warn(`${errors.length} errores: ${errors.slice(0, 3).join(', ')}`);
  }

  return imported;
}
