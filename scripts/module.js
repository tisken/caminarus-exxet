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

// Inject button in Actor Directory
Hooks.on('renderActorDirectory', (_app, html) => {
  if (!game.user.isGM || game.system?.id !== 'animabf') return;
  if (html.find('.animu-exxet-bulk-btn').length) return;

  const btn = $(`
    <button type="button" class="animu-exxet-bulk-btn">
      <i class="fas fa-file-import"></i>
      ${game.i18n.localize('ANIMU_EXXET.bulk.openBulkImport')}
    </button>
  `);

  btn.on('click', () => new BulkImportApp().render(true));

  // Insert in header actions, footer, or fallback
  const headerActions = html.find('.header-actions, .action-buttons, .directory-header .action-buttons');
  const footer = html.find('.directory-footer');

  if (headerActions.length) {
    headerActions.first().append(btn);
  } else if (footer.length) {
    footer.append(btn);
  } else {
    html.find('.directory-header').after(btn);
  }
});

// Inject button in Item Directory too
Hooks.on('renderItemDirectory', (_app, html) => {
  if (!game.user.isGM || game.system?.id !== 'animabf') return;
  if (html.find('.animu-exxet-bulk-btn').length) return;

  const btn = $(`
    <button type="button" class="animu-exxet-bulk-btn">
      <i class="fas fa-file-import"></i>
      ${game.i18n.localize('ANIMU_EXXET.bulk.openBulkImport')}
    </button>
  `);

  btn.on('click', () => new BulkImportApp().render(true));

  const headerActions = html.find('.header-actions, .action-buttons');
  const footer = html.find('.directory-footer');

  if (headerActions.length) {
    headerActions.first().append(btn);
  } else if (footer.length) {
    footer.append(btn);
  } else {
    html.find('.directory-header').after(btn);
  }
});
