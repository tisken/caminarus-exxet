import { importExcelFiles } from './excel-import.js';

const MODULE_ID = 'animu-exxet';

export class BulkImportApp {
  static show(targetFolder = null) {
    const folders = game.folders.filter(f => f.type === 'Actor');
    const folderOptions = folders.map(f => {
      let label = f.name.replace(/[_.]/g, ' ').replace(/\s+/g, ' ').trim();
      // Add indent for nested folders
      let depth = 0;
      let parent = f.folder;
      while (parent) {
        depth++;
        const pf = folders.find(x => x.id === parent);
        parent = pf ? pf.folder : null;
      }
      const indent = '\u00a0\u00a0'.repeat(depth);
      const selected = targetFolder?.id === f.id ? 'selected' : '';
      return `<option value="${f.id}" ${selected}>${indent}${label}</option>`;
    }).join('');

    const content = `
      <form style="display:grid; gap:0.75rem; padding:0.25rem;">
        <p style="margin:0;">${game.i18n.localize('ANIMU_EXXET.excel.description')}</p>
        <div class="form-group">
          <label><i class="fas fa-folder-open"></i> ${game.i18n.localize('ANIMU_EXXET.excel.selectFiles')}</label>
          <input type="file" name="files" accept=".xlsm,.xlsx" multiple="multiple" style="width:100%;" />
        </div>
        <div class="form-group">
          <label><i class="fas fa-folder"></i> ${game.i18n.localize('ANIMU_EXXET.excel.destination')}</label>
          <select name="folder" style="width:100%;">
            <option value="">${game.i18n.localize('ANIMU_EXXET.excel.rootActors')}</option>
            ${folderOptions}
          </select>
        </div>
      </form>
    `;

    let dlg = null;

    dlg = new foundry.applications.api.DialogV2({
      window: {
        title: game.i18n.localize('ANIMU_EXXET.excel.windowTitle'),
        icon: 'fas fa-file-import',
      },
      content,
      buttons: [
        {
          action: 'cancel',
          label: game.i18n.localize('ANIMU_EXXET.excel.cancel'),
          icon: 'fas fa-times',
        },
        {
          action: 'import',
          label: game.i18n.localize('ANIMU_EXXET.excel.accept'),
          icon: 'fas fa-check',
          default: true,
          callback: async () => {
            const html = dlg.element;
            if (!html) return;
            const fileInput = html.querySelector('input[name="files"]');
            const folderSelect = html.querySelector('select[name="folder"]');
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
      ],
    });

    dlg.render(true);
  }
}
