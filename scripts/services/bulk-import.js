import { importExcelFiles } from './excel-import.js';

const MODULE_ID = 'animu-exxet';

// Helper to get translation with fallback to Spanish
function t(key, fallback) {
  const result = game.i18n.localize(key);
  return result === key ? fallback : result;
}

export class BulkImportApp {
  static show(targetFolder = null) {
    const folders = game.folders.filter(f => f.type === 'Actor');
    const folderOptions = folders.map(f => {
      let label = f.name.replace(/[_.]/g, ' ').replace(/\s+/g, ' ').trim();
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
        <p style="margin:0;">Selecciona uno o varios archivos Excel (.xlsm) de Anima Beyond Fantasy.</p>
        <div class="form-group">
          <label><i class="fas fa-folder-open"></i> Archivos Excel</label>
          <div style="display:flex; gap:0.5rem; align-items:center;">
            <input type="file" id="animu-file-input" accept=".xlsm,.xlsx" multiple style="flex:1;" />
          </div>
          <div id="animu-file-list" style="margin-top:0.4rem; font-size:0.85em; color:var(--color-text-secondary); max-height:120px; overflow-y:auto;"></div>
        </div>
        <div class="form-group">
          <label><i class="fas fa-folder"></i> Carpeta de destino</label>
          <select name="folder" style="width:100%;">
            <option value="">Raíz de actores</option>
            ${folderOptions}
          </select>
        </div>
      </form>
    `;

    let dlg = null;
    let selectedFiles = [];

    dlg = new foundry.applications.api.DialogV2({
      window: {
        title: 'Importar fichas de Anima desde Excel',
        icon: 'fas fa-file-import',
      },
      content,
      buttons: [
        {
          action: 'cancel',
          label: 'Cancelar',
          icon: 'fas fa-times',
        },
        {
          action: 'import',
          label: 'Importar fichas',
          icon: 'fas fa-check',
          default: true,
          callback: async () => {
            const html = dlg.element;
            if (!html) return;

            const fileInput = html.querySelector('#animu-file-input');
            const newFiles = Array.from(fileInput?.files ?? []);
            const allFiles = [...selectedFiles, ...newFiles.filter(f => !selectedFiles.find(s => s.name === f.name))];

            const folderSelect = html.querySelector('select[name="folder"]');
            const folderId = folderSelect?.value;
            const folder = folderId ? game.folders.get(folderId) : null;

            if (!allFiles.length) {
              ui.notifications.warn('No has seleccionado ningún archivo.');
              return;
            }

            await importExcelFiles(allFiles, folder);
          }
        },
      ],
    });

    dlg.render(true);

    dlg.addEventListener('render', () => {
      const html = dlg.element;
      if (!html) return;

      const fileInput = html.querySelector('#animu-file-input');
      const fileList = html.querySelector('#animu-file-list');

      if (fileInput) {
        fileInput.multiple = true;

        fileInput.addEventListener('change', () => {
          const newFiles = Array.from(fileInput.files);
          for (const f of newFiles) {
            if (!selectedFiles.find(s => s.name === f.name)) {
              selectedFiles.push(f);
            }
          }
          if (fileList) {
            if (selectedFiles.length === 0) {
              fileList.textContent = '';
            } else {
              fileList.innerHTML = selectedFiles.map((f, i) =>
                `<div style="display:flex; justify-content:space-between; padding:1px 0;">
                  <span>📄 ${f.name}</span>
                  <span style="cursor:pointer; color:var(--color-text-secondary);" data-idx="${i}" class="animu-remove-file">✕</span>
                </div>`
              ).join('');
              fileList.querySelectorAll('.animu-remove-file').forEach(btn => {
                btn.addEventListener('click', () => {
                  selectedFiles.splice(parseInt(btn.dataset.idx), 1);
                  fileInput.dispatchEvent(new Event('change'));
                });
              });
            }
          }
        });
      }
    });
  }
}
