const MODULE_ID = 'animu-exxet';

async function getPackFolderTree(pack) {
  const index = await pack.getIndex({ fields: ['name', 'folder', 'type'] });
  const folders = [];
  const entries = [];

  for (const entry of index) {
    if (entry._id && entry.name) {
      entries.push(entry);
    }
  }

  const folderDocs = entries.filter(e => e.type === undefined || e instanceof Folder);
  const db = await pack.getDocuments();
  for (const doc of db) {
    if (doc.documentName === 'Folder' || doc instanceof Folder) {
      folders.push({ _id: doc.id, name: doc.name, folder: doc.folder });
    }
  }

  if (!folders.length) {
    for (const entry of index) {
      try {
        if (entry._id && !entry.type) {
          folders.push({ _id: entry._id, name: entry.name, folder: entry.folder ?? null });
        }
      } catch (e) { /* skip */ }
    }
  }

  return { folders, entryCount: entries.filter(e => e.type).length };
}

async function importDocumentsFromPack(pack, folderIds, targetFolder = null) {
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

  let imported = 0;
  const chunkSize = 10;
  const DocumentClass = pack.documentClass;

  for (let i = 0; i < docIds.length; i += chunkSize) {
    const chunk = docIds.slice(i, i + chunkSize);
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

function getChildFolderIds(folders, parentId) {
  const ids = new Set([parentId]);
  const findChildren = pid => {
    for (const f of folders) {
      if (f.folder === pid && !ids.has(f._id)) {
        ids.add(f._id);
        findChildren(f._id);
      }
    }
  };
  findChildren(parentId);
  return ids;
}

export class BulkImportApp extends Application {
  static get defaultOptions() {
    return foundry.utils.mergeObject(super.defaultOptions, {
      id: `${MODULE_ID}-bulk-import`,
      title: game.i18n.localize('ANIMU_EXXET.bulk.windowTitle'),
      template: `modules/${MODULE_ID}/templates/bulk-import.hbs`,
      width: 520,
      height: 'auto',
      classes: [MODULE_ID]
    });
  }

  async getData() {
    const packs = [];
    for (const pack of game.packs) {
      if (pack.metadata.packageName === MODULE_ID) {
        const { folders } = await getPackFolderTree(pack);
        const root = folders.find(f => f.folder === null);
        const children = folders.filter(f => f.folder === root?._id);

        const buildTree = (parent, depth = 0) => {
          const result = [{ ...parent, depth, indent: '\u00a0\u00a0'.repeat(depth) }];
          const kids = folders.filter(f => f.folder === parent._id).sort((a, b) => a.name.localeCompare(b.name));
          for (const kid of kids) {
            result.push(...buildTree(kid, depth + 1));
          }
          return result;
        };

        const tree = root ? buildTree(root) : [];

        packs.push({
          collection: pack.collection,
          label: pack.metadata.label,
          type: pack.metadata.type,
          folders: tree
        });
      }
    }

    const worldFolders = game.folders.filter(f => f.type === 'Actor' || f.type === 'Item');

    return { packs, worldFolders };
  }

  activateListeners(html) {
    super.activateListeners(html);

    html.find('[data-action="import-folder"]').on('click', async event => {
      const btn = event.currentTarget;
      const packId = btn.dataset.pack;
      const folderId = btn.dataset.folder;
      const recursive = btn.dataset.recursive === 'true';
      const pack = game.packs.get(packId);
      if (!pack) return;

      const worldFolderId = html.find(`[name="worldFolder-${packId}"]`).val();
      const worldFolder = worldFolderId ? game.folders.get(worldFolderId) : null;

      const { folders } = await getPackFolderTree(pack);
      const folderIds = recursive
        ? getChildFolderIds(folders, folderId)
        : new Set([folderId]);

      await importDocumentsFromPack(pack, folderIds, worldFolder);
    });

    html.find('[data-action="import-all"]').on('click', async event => {
      const packId = event.currentTarget.dataset.pack;
      const pack = game.packs.get(packId);
      if (!pack) return;

      const worldFolderId = html.find(`[name="worldFolder-${packId}"]`).val();
      const worldFolder = worldFolderId ? game.folders.get(worldFolderId) : null;

      const { folders } = await getPackFolderTree(pack);
      const allIds = new Set(folders.map(f => f._id));

      await importDocumentsFromPack(pack, allIds, worldFolder);
    });
  }
}

export function addBulkImportButton() {
  Hooks.on('renderCompendiumDirectory', (_app, html) => {
    if (!game.user.isGM || game.system?.id !== 'animabf') return;
    if (html.find('.animu-exxet-bulk-button').length) return;

    const button = $(`
      <button type="button" class="animu-exxet-bulk-button">
        <i class="fas fa-file-import"></i>
        ${game.i18n.localize('ANIMU_EXXET.bulk.openBulkImport')}
      </button>
    `);

    button.on('click', () => new BulkImportApp().render(true));
    html.find('.directory-footer').append(button);
  });
}
