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

function injectButton(html, cssClass, label, icon, onClick) {
  if (html.find(`.${cssClass}`).length) return;

  const btn = $(`
    <button type="button" class="${cssClass}" style="margin: 2px;">
      <i class="${icon}"></i> ${label}
    </button>
  `);
  btn.on('click', onClick);

  // Try multiple insertion points for v13/v14 compatibility
  const targets = [
    html.find('.header-actions'),
    html.find('.action-buttons'),
    html.find('.directory-footer'),
    html.find('[class*="footer"]'),
    html.find('[class*="header"] .flexrow'),
    html.find('[class*="header"]'),
  ];

  for (const target of targets) {
    if (target.length) {
      target.first().append(btn);
      return;
    }
  }

  // Last resort: append to the html element itself
  html.append(btn);
}

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

// Inject in Actor Directory
Hooks.on('renderActorDirectory', (_app, html) => {
  if (!game.user.isGM || game.system?.id !== 'animabf') return;
  injectButton(
    html,
    'animu-exxet-bulk-btn',
    game.i18n.localize('ANIMU_EXXET.bulk.openBulkImport'),
    'fas fa-file-import',
    () => new BulkImportApp().render(true)
  );
});

// Inject in Item Directory
Hooks.on('renderItemDirectory', (_app, html) => {
  if (!game.user.isGM || game.system?.id !== 'animabf') return;
  injectButton(
    html,
    'animu-exxet-bulk-btn',
    game.i18n.localize('ANIMU_EXXET.bulk.openBulkImport'),
    'fas fa-file-import',
    () => new BulkImportApp().render(true)
  );
});

// Also try the generic sidebar tab hook
Hooks.on('renderSidebarTab', (app, html) => {
  if (!game.user.isGM || game.system?.id !== 'animabf') return;
  const tabName = app.constructor?.name ?? app.tabName ?? '';
  if (!['ActorDirectory', 'ItemDirectory'].includes(tabName)) return;
  injectButton(
    html,
    'animu-exxet-bulk-btn',
    game.i18n.localize('ANIMU_EXXET.bulk.openBulkImport'),
    'fas fa-file-import',
    () => new BulkImportApp().render(true)
  );
});

// V2 Application hook for Foundry v14+
Hooks.on('changeSidebarTab', app => {
  if (!game.user.isGM || game.system?.id !== 'animabf') return;
  const tabName = app.constructor?.name ?? '';
  if (!['ActorDirectory', 'ItemDirectory'].includes(tabName)) return;

  // Wait for DOM to be ready
  setTimeout(() => {
    const el = app.element;
    if (!el) return;
    const html = $(el instanceof jQuery ? el : el);
    injectButton(
      html,
      'animu-exxet-bulk-btn',
      game.i18n.localize('ANIMU_EXXET.bulk.openBulkImport'),
      'fas fa-file-import',
      () => new BulkImportApp().render(true)
    );
  }, 100);
});
