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
  zeon: 'V48', act: 'F50', magicProjection: 'J48',
  summon: 'S50', control: 'X50', bind: 'S51', banish: 'X51',
  cv: 'H60', innate: 'O60',
  psychicPotential: 'J62', psychicProjection: 'K64',
  fatigue: 'H95', size: 'G93', movement: 'S93', regeneration: 'Q95',
  taEle: 'X32', taFri: 'AB32', taEne: 'AF32',
  zeonRegen: 'AD48',
  bind: 'AB50', banish: 'AH50',
  kiPoints: 'I35',
  kiAccFue: 'M37', kiAccDes: 'Q37', kiAccAgi: 'U37',
  kiAccCon: 'Y37', kiAccPod: 'AC37', kiAccVol: 'AC38',
  techniques: 'G43',
  psychicDisciplinesAlt: 'K66',
  psychicPowersAlt: 'J68',
  psychicLevel: 'I71',
  actionsPerTurn: 'AG95',
  languages: 'D112',
  secondarySkills: 'D98',
  advantages: 'K73', naturalAbilities: 'K76', special: 'G79',
  essentialAbilities: 'K84', powers: 'K87',
  kiSkills: 'H39', techniques: 'H43',
  magicLevel: 'G52',
  psychicDisciplines: 'H66', psychicPowers: 'H69',
};


// Dynamic cell finder - searches for labels in the sheet
function findCell(sheet, label, startRow = 1, endRow = 130, startCol = 1, endCol = 35) {
  const labelLower = label.toLowerCase();
  for (let r = startRow; r <= endRow; r++) {
    for (let c = startCol; c <= endCol; c++) {
      const ref = XLSX.utils.encode_cell({ r: r - 1, c: c - 1 });
      const cell = sheet[ref];
      if (cell && String(cell.v).toLowerCase().includes(labelLower)) {
        return { row: r, col: c, ref };
      }
    }
  }
  return null;
}

function cellAt(sheet, row, col) {
  const ref = XLSX.utils.encode_cell({ r: row - 1, c: col - 1 });
  const cell = sheet[ref];
  return cell ? cell.v : null;
}

function cellRight(sheet, row, col, offset = 1) {
  return cellAt(sheet, row, col + offset);
}

function cellBelow(sheet, row, col, offset = 1) {
  return cellAt(sheet, row + offset, col);
}

// Find value cell next to a label (searches right and below)
function findValue(sheet, label, startRow = 1, endRow = 130) {
  const found = findCell(sheet, label, startRow, endRow);
  if (!found) return null;
  // Try right neighbors
  for (let offset = 1; offset <= 5; offset++) {
    const v = cellRight(sheet, found.row, found.col, offset);
    if (v != null && String(v).trim() !== '') return v;
  }
  // Try below
  const v = cellBelow(sheet, found.row, found.col);
  if (v != null) return v;
  return null;
}

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

  // Dynamic fields (position varies between Excel versions)
  const dynSize = safeInt(findValue(sheet, 'Tamaño:', 85, 120));
  const dynMovement = safeInt(findValue(sheet, 'Tipo de movimiento:', 85, 120));
  const dynFatigue = safeInt(findValue(sheet, 'Cansancio:', 85, 120));
  const dynRegen = safeInt(findValue(sheet, 'Regeneración:', 85, 120));
  const dynActionsPerTurn = safeInt(findValue(sheet, 'Acciones por turno:', 85, 120));

  // Dynamic secondary skills - find the label then read the cell below
  const habSecCell = findCell(sheet, 'Habilidades secundarias:', 85, 120);
  const dynSecondarySkills = habSecCell ? safeStr(cellBelow(sheet, habSecCell.row, habSecCell.col - 1)) || safeStr(cellAt(sheet, habSecCell.row + 1, 4)) : '';

  // Dynamic text fields
  const dynAdvantages = safeStr(findValue(sheet, 'Ventajas y desventajas:', 65, 100));
  const dynNaturalAbilities = safeStr(findValue(sheet, 'Habilidades naturales:', 65, 100));
  const dynSpecial = safeStr(findValue(sheet, 'Especial:', 65, 100));
  const dynEssentialAbilities = safeStr(findValue(sheet, 'Habilidades esenciales:', 65, 100));
  const dynPowers = safeStr(findValue(sheet, 'Poderes:', 65, 100));
  const dynLanguages = safeStr(findValue(sheet, 'Lenguas:', 100, 130));
  const isBlock = defenseRaw.toLowerCase().includes('parada');

  const skills = parseSecondarySkills(dynSecondarySkills || getStr(CELLS.secondarySkills));


  // Build armor item from TA values
  const taValues = {
    cut: getInt(CELLS.taFil), impact: getInt(CELLS.taCon), thrust: getInt(CELLS.taPen),
    heat: getInt(CELLS.taCal), electricity: getInt(CELLS.taEle),
    cold: getInt(CELLS.taFri), energy: getInt(CELLS.taEne),
  };
  const items = [];
  if (Object.values(taValues).some(v => v > 0)) {
    items.push({
      name: getStr(CELLS.taLabel) || 'Armadura',
      type: 'armor',
      img: 'icons/equipment/chest/breastplate-cuirass-steel-grey.webp',
      system: {
        ...Object.fromEntries(Object.entries(taValues).map(([k, v]) => [k, { base: { value: v }, final: { value: 0 }, value: v }])),
        pierce: { base: { value: 0 }, final: { value: 0 }, value: 0 },
        integrity: { base: { value: 0 }, final: { value: 0 } },
        presence: { base: { value: 0 }, final: { value: 0 } },
        movementRestriction: { base: { value: 0 }, final: { value: 0 } },
        naturalPenalty: { base: { value: 0 }, final: { value: 0 } },
        wearArmorRequirement: { base: { value: 0 }, final: { value: 0 } },
        isEnchanted: { value: false }, type: { value: 'hard' },
        localization: { value: 'complete' }, quality: { value: 0 }, equipped: { value: true },
      },
    });
  }

  // Build notes from text fields
  // Use dynamic values for notes (handles shifted rows)
  const dynNoteValues = [
    [dynAdvantages || getStr(CELLS.advantages), 'Ventajas y desventajas'],
    [dynNaturalAbilities || getStr(CELLS.naturalAbilities), 'Habilidades naturales'],
    [dynEssentialAbilities || getStr(CELLS.essentialAbilities), 'Habilidades esenciales'],
    [dynPowers || getStr(CELLS.powers), 'Poderes'],
    [dynSpecial || getStr(CELLS.special), 'Especial'],
    [CELLS.kiSkills, 'Habilidades de Ki'],
    [CELLS.techniques, 'Técnicas'],
    [CELLS.magicLevel, 'Nivel de Magia'],
    [CELLS.psychicDisciplines, 'Disciplinas Psíquicas'],
    [CELLS.psychicPowers, 'Poderes Psíquicos'],
  ];
  const notes = [];
  for (const [val, label] of dynNoteValues) {
    if (val) notes.push({ _id: foundry.utils.randomID(), type: 'note', name: `${label}: ${val}`, system: {} });
  }

  // Build the actor data

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
        aspect: { hair: { value: '' }, eyes: { value: '' }, height: { value: '' }, weight: { value: '' }, age: { value: '' }, gender: { value: '' }, race: { value: getStr(CELLS.class) }, ethnicity: { value: '' }, appearance: { value: '' }, size: { value: String(dynSize || getInt(CELLS.size)) } },
        advantages: [], contacts: [], inventory: [],
        money: { cooper: { value: 0 }, silver: { value: 0 }, gold: { value: 0 } },
        description: { value: `<p>Importado desde ${fileName}</p><p>${dynLanguages || getStr(CELLS.languages)}</p>`, enriched: '' },
        disadvantages: [], elan: [],
        experience: { current: { value: 0 }, next: { value: 0 } },
        languages: { base: { value: '' }, others: [] },
        levels: [{ _id: foundry.utils.randomID(), type: 'level', name, flags: { version: 1 }, system: { level } }],
        notes,
        titles: [],
      },
      characteristics: {
        primaries: Object.fromEntries(
          Object.entries(primaries).map(([k, v]) => [k, { value: v, mod: calcMod(v) }])
        ),
        secondaries: {
          lifePoints: { value: getInt(CELLS.lifePoints), max: getInt(CELLS.lifePoints) },
          initiative: { base: { value: getInt(CELLS.initiative) }, final: { value: 0 } },
          fatigue: { value: dynFatigue || getInt(CELLS.fatigue), max: dynFatigue || getInt(CELLS.fatigue) },
          regenerationType: { mod: { value: dynRegen || getInt(CELLS.regeneration) }, final: { value: 0 } },
          regeneration: { normal: { value: 0, period: '' }, resting: { value: 0, period: '' }, recovery: { value: 0, period: '' } },
          movementType: { mod: { value: (dynMovement || getInt(CELLS.movement)) - primaries.agility }, final: { value: 0 } },
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
        zeonRegeneration: { base: { value: getInt(CELLS.zeonRegen) }, final: { value: 0 } },
        innateMagic: { main: { value: 0 }, alternative: { value: 0 } },
        magicProjection: (() => {
          const mpRaw = getStr(CELLS.magicProjection);
          const mpNums = mpRaw.match(/-?\d+/g) || [];
          const mpBase = parseInt(mpNums[0]) || 0;
          const mpOff = mpRaw.toLowerCase().includes('ofensiva') && mpNums.length >= 1 ? parseInt(mpNums[0]) || 0 : mpBase;
          const mpDef = mpRaw.toLowerCase().includes('defensiva') && mpNums.length >= 2 ? parseInt(mpNums[1]) || 0 : mpBase;
          return { base: { value: mpBase }, final: { value: 0 }, imbalance: { offensive: { base: { value: mpOff }, final: { value: 0 } }, defensive: { base: { value: mpDef }, final: { value: 0 } } } };
        })(),
        magicLevel: (() => {
          const mlRaw = getStr(CELLS.magicLevel).toLowerCase();
          const sphereMap = {esencia:'essence',agua:'water',tierra:'earth',creacion:'creation',oscuridad:'darkness',nigromancia:'necromancy',luz:'light',destruccion:'destruction',aire:'air',fuego:'fire',ilusion:'illusion',vacio:'destruction'};
          const spheres = Object.fromEntries(['essence','water','earth','creation','darkness','necromancy','light','destruction','air','fire','illusion'].map(k => [k, {value: 0}]));
          for (const [es, en] of Object.entries(sphereMap)) {
            const m = mlRaw.match(new RegExp(es + '[^,]*?(\\d+)'));
            if (!m) { const m2 = mlRaw.match(new RegExp('(\\d+)\\s*' + es)); if (m2) spheres[en].value = parseInt(m2[1]); }
            else spheres[en].value = parseInt(m[1]);
          }
          const total = Object.values(spheres).reduce((s, v) => s + v.value, 0);
          return { spheres, total: { value: total }, used: { value: total } };
        })(),
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
        kiAccumulation: {
          strength: { accumulated: { value: 0 }, base: { value: getInt(CELLS.kiAccFue) }, final: { value: 0 } },
          agility: { accumulated: { value: 0 }, base: { value: getInt(CELLS.kiAccAgi) }, final: { value: 0 } },
          dexterity: { accumulated: { value: 0 }, base: { value: getInt(CELLS.kiAccDes) }, final: { value: 0 } },
          constitution: { accumulated: { value: 0 }, base: { value: getInt(CELLS.kiAccCon) }, final: { value: 0 } },
          willPower: { accumulated: { value: 0 }, base: { value: getInt(CELLS.kiAccVol) }, final: { value: 0 } },
          power: { accumulated: { value: 0 }, base: { value: getInt(CELLS.kiAccPod) }, final: { value: 0 } },
          generic: { value: getInt(CELLS.kiPoints), max: getInt(CELLS.kiPoints) },
        },
      },
      psychic: {
        psychicPotential: { base: { value: getInt(CELLS.psychicPotential) }, final: { value: 0 } },
        psychicProjection: (() => {
          const ppRaw = getStr(CELLS.psychicProjection);
          const ppNums = ppRaw.match(/-?\d+/g) || [];
          const ppBase = parseInt(ppNums[0]) || 0;
          const ppOff = ppRaw.toLowerCase().includes('ofensiva') && ppNums.length >= 1 ? parseInt(ppNums[0]) || 0 : ppBase;
          const ppDef = ppRaw.toLowerCase().includes('defensiva') && ppNums.length >= 2 ? parseInt(ppNums[1]) || 0 : ppBase;
          return { base: { value: ppBase }, final: { value: 0 }, imbalance: { offensive: { base: { value: ppOff }, final: { value: 0 } }, defensive: { base: { value: ppDef }, final: { value: 0 } } } };
        })(),
        psychicPoints: { value: getInt(CELLS.cv), max: getInt(CELLS.cv) },
        psychicPowers: [], psychicDisciplines: [], mentalPatterns: [],
        innatePsychicPower: { amount: { value: getInt(CELLS.innate) } },
        // psychicLevel not directly mapped in animabf system
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
    items,
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
