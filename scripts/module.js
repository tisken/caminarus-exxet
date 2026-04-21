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

function injectButton(el) {
  if (!(el instanceof HTMLElement)) return;
  if (el.querySelector('.animu-exxet-bulk-btn')) return;

  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'animu-exxet-bulk-btn';
  btn.style.margin = '2px';
  btn.innerHTML = `<i class="fas fa-file-import"></i> ${game.i18n.localize('ANIMU_EXXET.excel.openImporter')}`;
  btn.addEventListener('click', () => BulkImportApp.show());

  const target =
    el.querySelector('.header-actions') ??
    el.querySelector('.action-buttons') ??
    el.querySelector('.directory-footer') ??
    el.querySelector('.directory-header');

  if (target) target.appendChild(btn);
  else el.prepend(btn);
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
  injectButton(html instanceof HTMLElement ? html : html[0] ?? html);
});
