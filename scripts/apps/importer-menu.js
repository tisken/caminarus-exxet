import { importAllDatasets, importDataset, loadIndex } from '../services/compendium-service.js';

const MODULE_ID = 'animu-exxet';

export class AnimuExxetImporterMenu extends Application {
  static get defaultOptions() {
    return foundry.utils.mergeObject(super.defaultOptions, {
      id: `${MODULE_ID}-importer`,
      title: game.i18n.localize('ANIMU_EXXET.ui.windowTitle'),
      template: `modules/${MODULE_ID}/templates/importer-menu.hbs`,
      width: 560,
      height: 'auto',
      classes: [MODULE_ID]
    });
  }

  async getData() {
    const index = await loadIndex();
    return {
      datasets: index.datasets ?? [],
      rebuildExisting: true
    };
  }

  activateListeners(html) {
    super.activateListeners(html);

    html.find('[data-action="import-one"]').on('click', async event => {
      const rebuildExisting = this.#readRebuildPreference(html);
      const datasetId = event.currentTarget.dataset.datasetId;
      await importDataset(datasetId, { rebuildExisting });
    });

    html.find('[data-action="import-all"]').on('click', async () => {
      const rebuildExisting = this.#readRebuildPreference(html);
      await importAllDatasets({ rebuildExisting });
    });
  }

  #readRebuildPreference(html) {
    return html.find('[name="rebuildExisting"]').is(':checked');
  }
}
