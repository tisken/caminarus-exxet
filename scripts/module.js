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
  // Foundry v13+ passes native DOM element, not jQuery
  const el = html instanceof HTMLElement ? html : html[0] ?? html;
  if (!el || !(el instanceof HTMLElement)) return;
  if (el.querySelector(`.${cssClass}`)) return;

  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = cssClass;
  btn.style.margin = '2px';
  btn.innerHTML = `<i class="${icon}"></i> ${label}`;
  btn.addEventListener('click', onClick);

  const target =
    el.querySelector('.header-actions') ??
    el.querySelector('.action-buttons') ??
    el.querySelector('.directory-footer') ??
    el.querySelector('[class*="footer"]') ??
    el.querySelector('.directory-header');

  if (target) {
    target.appendChild(btn);
  } else {
    el.prepend(btn);
  }
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
