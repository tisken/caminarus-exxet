const MODULE_ID = 'animu-exxet';

async function getCompendiumFolderActors(pack, folderId, recursive = false) {
  const index = await pack.getIndex({ fields: ['name', 'folder', 'type'] });
  const folders = await pack.getDocuments({ type: 'Folder' }).catch(() => []);

  const targetFolderIds = new Set([folderId]);
  if (recursive) {
    const allFolders = [];
    for (const entry of index) {
      if (entry.type === undefined) continue;
    }
    const packFolders = folders.length
      ? folders
      : Array.from(index.values()).filter(e => e instanceof Folder);

    const findChildren = parentId => {
      for (const f of packFolders) {
        if (f.folder === parentId) {
          targetFolderIds.add(f._id);
          findChildren(f._id);
        }
      }
    };
    findChildren(folderId);
  }

  const actorIds = [];
  for (const entry of index) {
    if (targetFolderIds.has(entry.folder)) {
      actorIds.push(entry._id);
    }
  }
  return actorIds;
}

async function importActorsToWorld(pack, actorIds, targetFolder = null) {
  if (!actorIds.length) {
    ui.notifications.warn(game.i18n.localize('ANIMU_EXXET.bulk.noActors'));
    return 0;
  }

  ui.notifications.info(
    game.i18n.format('ANIMU_EXXET.bulk.startImport', { count: actorIds.length })
  );

  const chunkSize = 10;
  let imported = 0;

  for (let i = 0; i < actorIds.length; i += chunkSize) {
    const chunk = actorIds.slice(i, i + chunkSize);
    const docs = await pack.getDocuments({ _id__in: chunk });

    for (const doc of docs) {
      const data = doc.toObject();
      delete data._id;
      if (targetFolder) data.folder = targetFolder.id;
      else data.folder = null;
      await Actor.create(data);
      imported++;
    }
  }

  ui.notifications.info(
    game.i18n.format('ANIMU_EXXET.bulk.finishImport', { count: imported })
  );
  return imported;
}

async function chooseWorldFolder() {
  const folders = game.folders.filter(f => f.type === 'Actor');
  if (!folders.length) return null;

  const options = folders.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
  const content = `
    <form>
      <div class="form-group">
        <label>${game.i18n.localize('ANIMU_EXXET.bulk.targetFolder')}</label>
        <select name="folder">
          <option value="">${game.i18n.localize('ANIMU_EXXET.bulk.rootFolder')}</option>
          ${options}
        </select>
      </div>
    </form>
  `;

  return new Promise(resolve => {
    new Dialog({
      title: game.i18n.localize('ANIMU_EXXET.bulk.chooseFolder'),
      content,
      buttons: {
        ok: {
          icon: '<i class="fas fa-check"></i>',
          label: game.i18n.localize('ANIMU_EXXET.bulk.import'),
          callback: html => {
            const folderId = html.find('[name=folder]').val();
            resolve(folderId ? game.folders.get(folderId) : null);
          }
        },
        cancel: {
          icon: '<i class="fas fa-times"></i>',
          label: game.i18n.localize('ANIMU_EXXET.bulk.cancel'),
          callback: () => resolve(undefined)
        }
      },
      default: 'ok'
    }).render(true);
  });
}

export async function bulkImportFolder(pack, folderId, recursive = false) {
  const targetFolder = await chooseWorldFolder();
  if (targetFolder === undefined) return;

  const actorIds = await getCompendiumFolderActors(pack, folderId, recursive);
  return importActorsToWorld(pack, actorIds, targetFolder);
}

export function addContextMenuOptions() {
  const modulePackName = `${MODULE_ID}.creatures-exxet`;

  Hooks.on('getCompendiumDirectoryFolderContext', (html, options) => {
    options.push(
      {
        name: game.i18n.localize('ANIMU_EXXET.bulk.importFolder'),
        icon: '<i class="fas fa-download"></i>',
        condition: li => {
          const pack = game.packs.get(modulePackName);
          return pack && game.user.isGM;
        },
        callback: async li => {
          const pack = game.packs.get(modulePackName);
          const folderId = li.data('folderId') || li.closest('[data-folder-id]')?.dataset?.folderId;
          if (pack && folderId) await bulkImportFolder(pack, folderId, false);
        }
      },
      {
        name: game.i18n.localize('ANIMU_EXXET.bulk.importFolderRecursive'),
        icon: '<i class="fas fa-layer-group"></i>',
        condition: li => {
          const pack = game.packs.get(modulePackName);
          return pack && game.user.isGM;
        },
        callback: async li => {
          const pack = game.packs.get(modulePackName);
          const folderId = li.data('folderId') || li.closest('[data-folder-id]')?.dataset?.folderId;
          if (pack && folderId) await bulkImportFolder(pack, folderId, true);
        }
      }
    );
  });
}
