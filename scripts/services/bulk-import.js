const MODULE_ID = 'animu-exxet';

async function getPackFolderTree(pack) {
  const index = await pack.getIndex({ fields: ['name', 'folder', 'type'] });
  const folders = [];

  try {
    const docs = await pack.getDocuments();
    for (const doc of docs) {
      if (doc.documentName === 'Folder' || doc instanceof Folder) {
        folders.push({ _id: doc.id, name: doc.name, folder: doc.folder });
      }
    }
  } catch (e) { /* pack may not support getDocuments for folders */ }

  return folders;
}

function getChildFolderIds(folders, parentId) {
  const ids = new Set([parentId]);
  const find = pid => {
    for (const f of folders) {
      if (f.folder === pid && !ids.has(f._id)) {
        ids.add(f._id);
        find(f._id);
      }
    }
  };
  find(parentId);
  return ids;
}

async function importFromPack(pack, folderIds, targetFolder) {
  const index = await pack.getIndex({ fields: ['name', 'folder', 'type'] });
  const targetSet = new Set(folderIds);

  const docIds = [];
  for (const entry of index) {
    if (targetSet.has(entry.folder) && entry.type) {
      docIds.push(entry._id);
    }
  }

  if (!docIds.length) {
    ui.notifications.warn(game.i18n.localize('ANIMU_EXXET.bulk.noActors'));
    return 0;
  }

  ui.notifications.info(
    game.i18n.format('ANIMU_EXXET.bulk.startImport', { count: docIds.length })
  );

  const DocumentClass = pack.documentClass;
  let imported = 0;

  for (let i = 0; i < docIds.length; i += 10) {
    const chunk = docIds.slice(i, i + 10);
    const docs = await pack.getDocuments({ _id__in: chunk });
    for (const doc of docs) {
      const data = doc.toObject();
      delete data._id;
      data.folder = targetFolder?.id ?? null;
      await DocumentClass.create(data);
      imported++;
    }
  }

  ui.notifications.info(
    game.i18n.format('ANIMU_EXXET.bulk.finishImport', { count: imported })
  );
  return imported;
}

export class BulkImportApp extends Application {
  constructor(options = {}) {
    super(options);
    this._targetFolder = options.targetFolder ?? null;
  }

  static get defaultOptions() {
    return foundry.utils.mergeObject(super.defaultOptions, {
      id: `${MODULE_ID}-bulk-import`,
      title: game.i18n.localize('ANIMU_EXXET.bulk.windowTitle'),
      template: `modules/${MODULE_ID}/templates/bulk-import.hbs`,
      width: 560,
      height: 'auto',
      classes: [MODULE_ID]
    });
  }

  async getData() {
    const packs = [];
    for (const pack of game.packs) {
      if (pack.metadata.packageName !== MODULE_ID) continue;

      const folders = await getPackFolderTree(pack);
      const root = folders.find(f => f.folder === null);

      const buildTree = (parent, depth = 0) => {
        const result = [{ ...parent, depth, indent: '\u00a0\u00a0\u00a0'.repeat(depth) }];
        const kids = folders.filter(f => f.folder === parent._id).sort((a, b) => a.name.localeCompare(b.name));
        for (const kid of kids) result.push(...buildTree(kid, depth + 1));
        return result;
      };

      packs.push({
        collection: pack.collection,
        label: pack.metadata.label,
        type: pack.metadata.type,
        folders: root ? buildTree(root) : []
      });
    }

    return {
      packs,
      targetFolderName: this._targetFolder?.name ?? game.i18n.localize('ANIMU_EXXET.bulk.rootFolder'),
      targetFolderId: this._targetFolder?.id ?? ''
    };
  }

  activateListeners(html) {
    super.activateListeners(html);

    html.find('[data-action="import-folder"]').on('click', async event => {
      const btn = event.currentTarget;
      const pack = game.packs.get(btn.dataset.pack);
      if (!pack) return;

      const folderId = btn.dataset.folder;
      const recursive = btn.dataset.recursive === 'true';
      const folders = await getPackFolderTree(pack);
      const ids = recursive ? getChildFolderIds(folders, folderId) : new Set([folderId]);

      await importFromPack(pack, ids, this._targetFolder);
    });

    html.find('[data-action="import-all"]').on('click', async event => {
      const pack = game.packs.get(event.currentTarget.dataset.pack);
      if (!pack) return;

      const folders = await getPackFolderTree(pack);
      const allIds = new Set(folders.map(f => f._id));

      await importFromPack(pack, allIds, this._targetFolder);
    });
  }
}
