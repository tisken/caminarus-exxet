import { AnimuExxetImporterMenu } from './apps/importer-menu.js';
import { ensureRuntimeBestiaryCompendium, loadIndex } from './services/compendium-service.js';

const MODULE_ID = 'animu-exxet';

const openImporter = () => new AnimuExxetImporterMenu().render(true);

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

  game.settings.register(MODULE_ID, 'runtimePackVersion', {
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
      return;
    }

    if (game.user.isGM) {
      await ensureRuntimeBestiaryCompendium(index);
    }
  } catch (error) {
    console.error(`${MODULE_ID} | Error loading generated index`, error);
  }
});

Hooks.on('renderCompendiumDirectory', (_app, html) => {
  if (!game.user.isGM || game.system?.id !== 'animabf') return;
  if (html.find('.animu-exxet-directory-button').length) return;

  const button = $(`
    <button type="button" class="animu-exxet-directory-button">
      <i class="fas fa-dragon"></i>
      ${game.i18n.localize('ANIMU_EXXET.ui.openImporter')}
    </button>
  `);

  button.on('click', openImporter);
  html.find('.directory-footer').append(button);
});
