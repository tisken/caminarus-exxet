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

Hooks.on('renderCompendiumDirectory', (_app, html) => {
  if (!game.user.isGM || game.system?.id !== 'animabf') return;
  if (html.find('.animu-exxet-directory-button').length) return;

  const footer = html.find('.directory-footer');

  const importerBtn = $(`
    <button type="button" class="animu-exxet-directory-button">
      <i class="fas fa-dragon"></i>
      ${game.i18n.localize('ANIMU_EXXET.ui.openImporter')}
    </button>
  `);
  importerBtn.on('click', () => new AnimuExxetImporterMenu().render(true));
  footer.append(importerBtn);

  const bulkBtn = $(`
    <button type="button" class="animu-exxet-directory-button animu-exxet-bulk-button">
      <i class="fas fa-file-import"></i>
      ${game.i18n.localize('ANIMU_EXXET.bulk.openBulkImport')}
    </button>
  `);
  bulkBtn.on('click', () => new BulkImportApp().render(true));
  footer.append(bulkBtn);
});
