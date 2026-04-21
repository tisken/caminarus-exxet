import { importExcelFiles } from './excel-import.js';

const MODULE_ID = 'animu-exxet';

export class BulkImportApp {
  static show(targetFolder = null) {
    const folders = game.folders.filter(f => f.type === 'Actor');
    const folderOptions = folders.map(f =>
      `<option value="${f.id}" ${targetFolder?.id === f.id ? 'selected' : ''}>${f.name}</option>`
    ).join('');

    const content = `
      <form class="animu-exxet-excel-import" style="display:grid; gap:0.75rem;">
        <p style="margin:0;">${game.i18n.localize('ANIMU_EXXET.excel.description')}</p>
        <div class="form-group">
          <label>${game.i18n.localize('ANIMU_EXXET.excel.selectFiles')}</label>
          <input type="file" name="files" accept=".xlsm,.xlsx" multiple style="width:100%;" />
        </div>
        <div class="form-group">
          <label>${game.i18n.localize('ANIMU_EXXET.bulk.targetFolder')}</label>
          <select name="folder" style="width:100%;">
            <option value="">${game.i18n.localize('ANIMU_EXXET.bulk.rootFolder')}</option>
            ${folderOptions}
          </select>
        </div>
      </form>
    `;

    const dialog = new foundry.applications.api.DialogV2({
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
          callback: async (event, button, dlg) => {
            const html = dlg.element;
            const fileInput = html.querySelector('input[name="files"]');
            const folderSelect = html.querySelector('select[name="folder"]');
            const files = Array.from(fileInput?.files ?? []);
            const folderId = folderSelect?.value;
            const folder = folderId ? game.folders.get(folderId) : null;

            if (!files.length) {
              ui.notifications.warn(game.i18n.localize('ANIMU_EXXET.excel.noFiles'));
              return false;
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
    });

    dialog.render(true);
  }
}
