import { BulkImportApp } from './services/bulk-import.js';

const MODULE_ID = 'animu-exxet';

const registerSettings = () => {
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
  btn.innerHTML = `<i class="fas fa-file-import"></i> Multiimport fichas Excel`;
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
  }
});

Hooks.on('renderActorDirectory', (_app, html) => {
  if (!game.user.isGM || game.system?.id !== 'animabf') return;
  injectButton(html instanceof HTMLElement ? html : html[0] ?? html);
});
