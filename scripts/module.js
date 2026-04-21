import { AnimuExxetImporterMenu } from './apps/importer-menu.js';
import { loadIndex } from './services/compendium-service.js';
import { BulkImportApp } from './services/bulk-import.js';

const MODULE_ID = 'animu-exxet';

const registerSettings = () => {
  game.settings.registerMenu(MODULE_ID, 'importer', {
    name: 'ANIMU_EXXET.settings.importer.name',
    label: 'ANIMU_EXXET.settings.importer.label',
    hint: 'ANIMU_EXXET.settings.importer.hint',
    icon: 'fas fa-dragon',
    type: AnimuExxetImporterMenu,
    restricted: true
  });

  game.settings.register(MODULE_ID, 'lastImportAt', {
    scope: 'world',
    config: false,
    type: String,
    default: ''
  });
};

Hooks.once('init', () => {
  registerSettings();
});

Hooks.once('ready', async () => {
  if (game.system?.id !== 'animabf') {
    ui.notifications.warn(game.i18n.localize('ANIMU_EXXET.notifications.missingSystem'));
    return;
  }

  try {
    const index = await loadIndex();
    if (!index.datasets?.length) {
      ui.notifications.warn(game.i18n.localize('ANIMU_EXXET.notifications.emptyIndex'));
    }
  } catch (error) {
    console.error(`${MODULE_ID} | Error loading generated index`, error);
  }
});

// Context menu on Actor Directory folders
Hooks.on('getActorDirectoryFolderContext', (html, options) => {
  if (!game.user.isGM) return;

  options.push({
    name: game.i18n.localize('ANIMU_EXXET.bulk.importToFolder'),
    icon: '<i class="fas fa-file-import"></i>',
    callback: li => {
      const folderId = li.data('folderId') ?? li.closest('[data-folder-id]')?.dataset?.folderId;
      const folder = game.folders.get(folderId);
      new BulkImportApp({ targetFolder: folder }).render(true);
    }
  });
});

// Also add to Item Directory folders
Hooks.on('getItemDirectoryFolderContext', (html, options) => {
  if (!game.user.isGM) return;

  options.push({
    name: game.i18n.localize('ANIMU_EXXET.bulk.importToFolder'),
    icon: '<i class="fas fa-file-import"></i>',
    callback: li => {
      const folderId = li.data('folderId') ?? li.closest('[data-folder-id]')?.dataset?.folderId;
      const folder = game.folders.get(folderId);
      new BulkImportApp({ targetFolder: folder }).render(true);
    }
  });
});
