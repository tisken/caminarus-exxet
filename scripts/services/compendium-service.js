const MODULE_ID = 'animu-exxet';
const INDEX_PATH = `modules/${MODULE_ID}/data/generated/index.json`;

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

const ensureCompendium = async ({ dataset, rebuildExisting }) => {
  const packName = sanitizePackName(`${MODULE_ID}_${dataset.id}`);
  const packLabel = dataset.compendiumLabel ?? dataset.label;
  const existingPack = game.packs.find(
    pack => pack.collection === `world.${packName}` || pack.metadata.name === packName
  );

  if (existingPack && rebuildExisting) {
    await existingPack.deleteCompendium();
  } else if (existingPack) {
    return { pack: existingPack, rebuilt: false };
  }

  const pack = await CompendiumCollection.createCompendium({
    label: packLabel,
    name: packName,
    type: 'Actor',
    package: 'world',
    system: 'animabf'
  });

  return { pack, rebuilt: true };
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
    const chunkSize = 25;
    for (let i = 0; i < documents.length; i += chunkSize) {
      await Actor.createDocuments(documents.slice(i, i + chunkSize), {
        pack: pack.collection,
        keepId: false
      });
    }
  }

  await game.settings.set(MODULE_ID, 'lastImportAt', new Date().toISOString());

  ui.notifications.info(
    game.i18n.format('ANIMU_EXXET.notifications.finishImport', {
      label: dataset.label,
      count: documents.length,
      pack: pack.title
    })
  );

  return { count: documents.length, dataset, pack };
};

export const importAllDatasets = async (options = {}) => {
  const index = await loadIndex();
  const results = [];

  for (const dataset of index.datasets) {
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
