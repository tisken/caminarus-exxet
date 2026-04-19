const MODULE_ID = 'animu-exxet';
const INDEX_PATH = `modules/${MODULE_ID}/data/generated/index.json`;
const RUNTIME_PACK_LABEL = 'Creatures Exxet';
const RUNTIME_PACK_NAME = 'animu_exxet_creatures_exxet';
const ROOT_FOLDER_NAME = RUNTIME_PACK_LABEL;
const FOLDER_SEPARATOR = '#/CF_SEP/';

let indexCache;
const datasetCache = new Map();

const sanitizePackName = value =>
  value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');

const fetchJson = async path => {
  const response = await fetch(path, { cache: 'no-store' });
  if (!response.ok) throw new Error(`Unable to fetch ${path}: ${response.status}`);
  return response.json();
};

export const loadIndex = async () => {
  if (indexCache) return indexCache;
  indexCache = await fetchJson(INDEX_PATH);
  return indexCache;
};

export const loadDataset = async datasetId => {
  if (datasetCache.has(datasetId)) return datasetCache.get(datasetId);

  const index = await loadIndex();
  const datasetMeta = index.datasets.find(dataset => dataset.id === datasetId);
  if (!datasetMeta) throw new Error(`Dataset not found: ${datasetId}`);

  const dataset = await fetchJson(`modules/${MODULE_ID}/data/generated/${datasetMeta.filename}`);
  datasetCache.set(datasetId, dataset);
  return dataset;
};

const getRuntimePack = () =>
  game.packs.find(
    pack => pack.collection === `world.${RUNTIME_PACK_NAME}` || pack.metadata?.name === RUNTIME_PACK_NAME
  );

const buildRuntimeFolders = index => {
  const rootId = foundry.utils.randomID();
  const folderIds = new Map();
  const folders = [
    {
      _id: rootId,
      name: ROOT_FOLDER_NAME,
      type: 'Actor',
      sorting: 'a',
      folder: null,
      sort: 0,
      color: '#000000',
      flags: {}
    }
  ];

  for (const [datasetIndex, dataset] of index.datasets.entries()) {
    const folderId = foundry.utils.randomID();
    folderIds.set(dataset.id, folderId);
    folders.push({
      _id: folderId,
      name: dataset.label,
      type: 'Actor',
      sorting: 'a',
      folder: rootId,
      sort: (datasetIndex + 1) * 10,
      color: '#000000',
      flags: {}
    });
  }

  return { folders, folderIds };
};

const sanitizeEmbeddedItem = item => {
  const prepared = foundry.utils.deepClone(item);
  delete prepared._id;
  delete prepared._key;
  delete prepared._stats;
  return prepared;
};

const prepareRuntimeActor = ({ document, folderId, folderPath, sort }) => {
  const actor = foundry.utils.deepClone(document);
  delete actor._id;
  delete actor._key;
  delete actor._stats;
  actor.folder = folderId;
  actor.sort = sort;
  actor.flags ??= {};
  actor.flags.core ??= {};
  actor.flags.cf = {
    ...(actor.flags.cf ?? {}),
    id: actor.flags?.cf?.id ?? `temp_${foundry.utils.randomID(10)}`,
    path: folderPath,
    color: actor.flags?.cf?.color ?? '#000000'
  };
  actor.items = (actor.items ?? []).map(sanitizeEmbeddedItem);
  return actor;
};

const createRuntimeActors = async ({ pack, index, folderIds }) => {
  const documents = [];

  for (const datasetMeta of index.datasets) {
    const dataset = await loadDataset(datasetMeta.id);
    const folderId = folderIds.get(datasetMeta.id);
    const folderPath = `${ROOT_FOLDER_NAME}${FOLDER_SEPARATOR}${datasetMeta.label}`;

    for (const [documentIndex, document] of dataset.documents.entries()) {
      documents.push(
        prepareRuntimeActor({
          document,
          folderId,
          folderPath,
          sort: documentIndex * 10
        })
      );
    }
  }

  const chunkSize = 25;
  for (let index = 0; index < documents.length; index += chunkSize) {
    const chunk = documents.slice(index, index + chunkSize);
    await Actor.createDocuments(chunk, { pack: pack.collection, keepId: false });
  }

  return documents.length;
};

export const ensureRuntimeBestiaryCompendium = async (index = null) => {
  const resolvedIndex = index ?? (await loadIndex());
  const moduleVersion = game.modules.get(MODULE_ID)?.version ?? '';
  const builtVersion = game.settings.get(MODULE_ID, 'runtimePackVersion');
  const existingPack = getRuntimePack();

  let rebuildPack = !existingPack || builtVersion !== moduleVersion;
  if (existingPack && !rebuildPack) {
    const existingIndex = await existingPack.getIndex({ fields: ['folder'] });
    rebuildPack = existingIndex.size === 0;
  }

  if (!rebuildPack) return existingPack;

  ui.notifications.info(
    game.i18n.format('ANIMU_EXXET.notifications.startRuntimePack', {
      label: RUNTIME_PACK_LABEL
    })
  );

  if (existingPack) {
    await existingPack.deleteCompendium();
  }

  const pack = await CompendiumCollection.createCompendium({
    label: RUNTIME_PACK_LABEL,
    name: RUNTIME_PACK_NAME,
    type: 'Actor',
    package: 'world',
    system: 'animabf'
  });

  const { folders, folderIds } = buildRuntimeFolders(resolvedIndex);
  await Folder.createDocuments(folders, { pack: pack.collection, keepId: true });
  const count = await createRuntimeActors({ pack, index: resolvedIndex, folderIds });

  await game.settings.set(MODULE_ID, 'runtimePackVersion', moduleVersion);
  ui.notifications.info(
    game.i18n.format('ANIMU_EXXET.notifications.finishRuntimePack', {
      label: RUNTIME_PACK_LABEL,
      count,
      pack: pack.title
    })
  );

  return pack;
};

const ensureCompendium = async ({ dataset, rebuildExisting }) => {
  const packName = sanitizePackName(`${MODULE_ID}_${dataset.id}`);
  const packLabel = dataset.compendiumLabel ?? dataset.label;
  const existingPack = game.packs.find(
    pack => pack.collection === `world.${packName}` || pack.metadata.name === packName
  );

  if (existingPack && rebuildExisting) {
    await existingPack.deleteCompendium();
  } else if (existingPack) {
    return {
      pack: existingPack,
      rebuilt: false
    };
  }

  const pack = await CompendiumCollection.createCompendium({
    label: packLabel,
    name: packName,
    type: 'Actor',
    package: 'world',
    system: 'animabf'
  });

  return {
    pack,
    rebuilt: true
  };
};

const storeImportTimestamp = async () => {
  await game.settings.set(MODULE_ID, 'lastImportAt', new Date().toISOString());
};

export const importDataset = async (datasetId, options = {}) => {
  const { rebuildExisting = true } = options;
  const dataset = await loadDataset(datasetId);

  ui.notifications.info(
    game.i18n.format('ANIMU_EXXET.notifications.startImport', { label: dataset.label })
  );

  const { pack, rebuilt } = await ensureCompendium({ dataset, rebuildExisting });
  let documents = dataset.documents.map(document =>
    foundry.utils.deepClone(document)
  );

  if (!rebuilt && !rebuildExisting) {
    const index = await pack.getIndex({ fields: ['name'] });
    const existingNames = new Set(Array.from(index.values()).map(entry => entry.name));
    documents = documents.filter(document => !existingNames.has(document.name));
  }

  if (documents.length) {
    await Actor.createDocuments(documents, { pack: pack.collection, keepId: false });
  }
  await storeImportTimestamp();

  ui.notifications.info(
    game.i18n.format('ANIMU_EXXET.notifications.finishImport', {
      label: dataset.label,
      count: documents.length,
      pack: pack.title
    })
  );

  return {
    count: documents.length,
    dataset,
    pack
  };
};

export const importAllDatasets = async (options = {}) => {
  const index = await loadIndex();
  const results = [];

  for (const dataset of index.datasets) {
    // Import sequentially to keep Foundry document creation predictable.
    const result = await importDataset(dataset.id, options);
    results.push(result);
  }

  const totalCount = results.reduce((sum, result) => sum + result.count, 0);
  ui.notifications.info(
    game.i18n.format('ANIMU_EXXET.notifications.finishAll', {
      count: totalCount,
      packs: results.length
    })
  );

  return results;
};
