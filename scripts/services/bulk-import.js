import { importExcelFiles } from './excel-import.js';

const MODULE_ID = 'animu-exxet';

export class BulkImportApp extends foundry.applications.api.DialogV2 {
  static async show(targetFolder = null) {
    const folders = game.folders.filter(f => f.type === 'Actor');
    const folderOptions = folders.map(f =>
      `<option value="${f.id}" ${targetFolder?.id === f.id ? 'selected' : ''}>${f.name}</option>`
    ).join('');

    const content = `
      <form class="animu-exxet-excel-import">
        <p>${game.i18n.localize('ANIMU_EXXET.excel.description')}</p>
        <div class="form-group">
          <label>${game.i18n.localize('ANIMU_EXXET.excel.selectFiles')}</label>
          <input type="file" name="files" accept=".xlsm,.xlsx" multiple />
        </div>
        <div class="form-group">
          <label>${game.i18n.localize('ANIMU_EXXET.bulk.targetFolder')}</label>
          <select name="folder">
            <option value="">${game.i18n.localize('ANIMU_EXXET.bulk.rootFolder')}</option>
            ${folderOptions}
          </select>
        </div>
      </form>
    `;

    return new foundry.applications.api.DialogV2({
      window: {
        title: game.i18n.localize('ANIMU_EXXET.excel.windowTitle'),
        icon: 'fas fa-file-import',
      },
      content,
      buttons: [
        {
          action: 'import',
          label: game.i18n.localize('ANIMU_EXXET.excel.importButton'),
          icon: 'fas fa-file-import',
          default: true,
          callback: async (event, button, dialog) => {
            const form = dialog.querySelector('form');
            const fileInput = form.querySelector('input[name="files"]');
            const folderSelect = form.querySelector('select[name="folder"]');
            const files = Array.from(fileInput?.files ?? []);
            const folderId = folderSelect?.value;
            const folder = folderId ? game.folders.get(folderId) : null;

            if (!files.length) {
              ui.notifications.warn(game.i18n.localize('ANIMU_EXXET.excel.noFiles'));
              return;
            }

            await importExcelFiles(files, folder);
          }
        },
        {
          action: 'cancel',
          label: game.i18n.localize('ANIMU_EXXET.bulk.cancel'),
          icon: 'fas fa-times',
        }
      ],
    }).render(true);
  }
}
