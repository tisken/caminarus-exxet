# Entorno de desarrollo y referencias

Guía de rutas, fuentes, proyectos relacionados y flujo de trabajo para `animu-exxet`.

## Estructura de directorios

### `/animu-exxet/` — el addon de Foundry (este repo)

```
animu-exxet/
├── data/
│   ├── generated/          # JSON generados por generate_bestiary.py
│   │   ├── index.json      # índice maestro de todos los datasets
│   │   ├── *.actors.json   # documentos de actor listos para Foundry
│   │   └── *.records.json  # registros de depuración con campos crudos
│   └── reference/
│       └── animabf-template.json   # plantilla del sistema animabf
├── docs/
│   ├── roadmap.md          # mejoras pendientes del addon
│   └── DEVELOPMENT.md      # este archivo
├── lang/
│   └── es.json             # traducciones del módulo
├── packs/
│   └── creatures-exxet/    # compendio estático exportado (JSON por actor y carpeta)
├── scripts/
│   ├── module.js           # punto de entrada del módulo en Foundry
│   ├── apps/
│   │   └── importer-menu.js
│   └── services/
│       └── compendium-service.js
├── styles/
│   └── animu-exxet.css
├── templates/
│   └── importer-menu.hbs
├── tests/
│   └── test_generated_data.py   # tests de integridad sobre los JSON generados
├── tools/
│   └── generate_bestiary.py     # generador principal de fichas
├── module.json             # manifiesto de Foundry
└── README.md
```

### `/animu/` — proyecto padre (RAG + generación)

El proyecto padre es un RAG local para consulta sobre el corpus de Anima Beyond Fantasy.
`animu-exxet` vive como subdirectorio dentro de él (`/animu/animu-exxet/`).

```
/animu/
├── animu-exxet/            # ← este addon (submódulo / subdirectorio)
├── data/
│   ├── docs/               # PDFs y docx originales de los manuales
│   ├── docs_md/            # Markdown generado desde los PDFs (corpus operativo)
│   └── rag.db              # base de datos SQLite del RAG
├── docs/
│   ├── ARCHITECTURE.md     # arquitectura del RAG
│   ├── EXTRACTION_NOTES.md # notas sobre extracción y limpieza OCR
│   └── MODEL_NOTES.md      # notas sobre modelos y retrieval
├── qa/                     # benchmarks de calidad del RAG
├── src/                    # código Python del RAG
├── tests/                  # tests del RAG
├── web/                    # interfaz web del RAG
├── .env / .env.example     # configuración de Ollama, modelos, etc.
├── requirements.txt
└── README.md
```

## Fuentes de datos

### PDFs originales → `/animu/data/docs/`

Manuales en PDF (algunos `_unlocked`) que sirven como fuente primaria:

| Archivo | Manual |
|---------|--------|
| `Anima Beyond Fantasy - Core Exxet.pdf` | Core Exxet |
| `Anima Beyond Fantasy - Los que caminaron con nosotros_unlocked.pdf` | Los que caminaron con nosotros |
| `ABF_Complemento_Web_Vol1.pdf` | Complemento Web Vol. 1 |
| `ABF_Complemento_Web_Vol2.pdf` | Complemento Web Vol. 2 (sin fichas aún) |
| `ABF_Complemento_Web_Vol3.pdf` | Complemento Web Vol. 3 (sin fichas aún) |
| `Anima Gate of Memories - Guia_del_Mundo_Perfecto.pdf` | Guía del Mundo Perfecto |
| `Dramatis personae.pdf` | Dramatis Personae |
| `DramatisPersonaeVolumen2.pdf` | Dramatis Personae Vol. 2 |
| `Anima_Pantalla_del_Director_unlocked.pdf` | Pantalla del Director |
| `DRAVENOR_Ejercito_regular_de_La_Maquina_Parte_1.pdf` | Dravenor Parte 1 |
| `DRAVENOR_Ejercito_regular_de_La_Maquina_Parte_2.pdf` | Dravenor Parte 2 |
| `DRAVENOR_Ejercito_regular_de_La_Maquina_Parte_3.pdf` | Dravenor Parte 3 |
| `Anima Beyond Fantasy - Gaia Volumen I  - Más Allá de los Sueños_unlocked.pdf` | Gaia Vol. I |
| `Anima Beyond Fantasy - Gaia Volumen II - Más Allá del espejo_unlocked.pdf` | Gaia Vol. II |
| `ABF_Ficha_Etheldrea.pdf` | Ficha suelta: Etheldrea |
| `ABF_Ficha_Jigoku.pdf` | Ficha suelta: Jigoku No Kami |
| `ABF_Ficha_Orochi.pdf` | Ficha suelta: Orochi |
| `ABF_Ficha_Stravos.pdf` | Ficha suelta: Stravos Veritas |
| `ABF_Pazusu.pdf` | Ficha suelta: Pazusu |
| `Anima Beyond Fantasy - Arcana Exxet_unlocked.pdf` | Arcana Exxet (sin fichas) |
| `Anima Beyond Fantasy - Dominus Exxet - Los Dominios del Ki_unlocked.pdf` | Dominus Exxet (sin fichas) |
| `Anima Beyond Fantasy - Prometheum exxet.pdf` | Prometheum Exxet (sin fichas) |
| `Anima Beyond Fantasy - Gates of Memories.pdf` | Gates of Memories (sin fichas) |
| `Dramatis_Personae_-_Organizaciones.pdf` | Organizaciones (sin fichas) |
| `Info_general.docx` | Documento general de referencia |

### Markdown extraído → `/animu/data/docs_md/`

Versiones `.md` generadas desde los PDFs con el comando del RAG:

```bash
cd /animu && source .venv/bin/activate
python -m src.main export-md --source data/docs --output-dir data/docs_md --overwrite
```

Estos `.md` son la fuente que lee `generate_bestiary.py`. La ruta por defecto que busca el generador es:

```python
Path("/animu/data/docs_md") / filename
```

Con fallback a `MODULE_ROOT.parent / "data/docs_md" / filename`.

## Documentación del proyecto

| Archivo | Ubicación | Contenido |
|---------|-----------|-----------|
| `README.md` | `/animu-exxet/README.md` | Descripción del addon, instalación y uso en Foundry |
| `roadmap.md` | `/animu-exxet/docs/roadmap.md` | Mejoras pendientes del addon |
| `DEVELOPMENT.md` | `/animu-exxet/docs/DEVELOPMENT.md` | Este archivo |
| `README.md` | `/animu/README.md` | Descripción del RAG, instalación y comandos |
| `ARCHITECTURE.md` | `/animu/docs/ARCHITECTURE.md` | Arquitectura del RAG, mapa de módulos, flujos |
| `EXTRACTION_NOTES.md` | `/animu/docs/EXTRACTION_NOTES.md` | Notas sobre extracción OCR y limpieza del corpus |
| `MODEL_NOTES.md` | `/animu/docs/MODEL_NOTES.md` | Notas sobre modelos, retrieval y evaluación |

## Proyectos de referencia en `/tmp/`

Estos repos se clonaron como referencia durante el desarrollo:

### `/tmp/animabf/` y `/tmp/AnimaBeyondFoundry/`

Repo oficial del sistema `animabf` para Foundry VTT.
- GitHub: `https://github.com/AnimaBeyondDevelop/AnimaBeyondFoundry`
- Contiene `src/template.json` → base para `data/reference/animabf-template.json`
- Contiene `src/system.json` → manifiesto del sistema (versión, compatibilidad)
- Útil para entender la estructura de datos de actores, ítems y campos del sistema

### `/tmp/abf-compendiums/`

Módulo comunitario `abf-compendiums` con compendios de conjuros, armas, etc.
- Contiene `packs/` con compendios existentes del sistema
- Contiene `Images/` e `Icons/` con recursos gráficos
- Útil como referencia de cómo otros módulos organizan compendios para `animabf`

### `/tmp/abf_reference.json`

Extracto de referencia con datos de criaturas del sistema, usado para validación cruzada.

### `/tmp/real_template.json`

Copia de la plantilla real de `animabf` (`template.json`), usada para generar `animabf-template.json`.

### `/tmp/animu_md_smoke/` y `/tmp/animu_md_smoke_pdf/`

Directorios temporales de pruebas de humo para la exportación de Markdown.

### `/tmp/animu_md_check/`

Directorio temporal con `.md` regenerados para verificar cambios en la extracción.

## Flujo de generación

```
PDFs originales (/animu/data/docs/)
        │
        ▼
  export-md del RAG (/animu/)
        │
        ▼
Markdown extraído (/animu/data/docs_md/)
        │
        ▼
  generate_bestiary.py (/animu-exxet/tools/)
        │
        ├──▶ data/generated/*.actors.json   (datasets para Foundry)
        ├──▶ data/generated/*.records.json  (registros de depuración)
        ├──▶ data/generated/index.json      (índice maestro)
        └──▶ packs/creatures-exxet/         (compendio estático)
```

### Comandos de generación

```bash
cd /animu-exxet
python tools/generate_bestiary.py
```

### Comandos de test

```bash
cd /animu-exxet
python -m pytest tests/test_generated_data.py -v
```

## Conteo actual de fichas por libro

| Dataset | Fichas |
|---------|--------|
| Core Exxet | 20 |
| Los que caminaron con nosotros | 92 |
| Complemento Web Vol. 1 | 5 |
| Guía del Mundo Perfecto | 20 |
| Dramatis Personae | 11 |
| Dramatis Personae Vol. 2 | 11 |
| Pantalla del Director | 33 |
| Dravenor Parte 1 | 5 |
| Dravenor Parte 2 | 5 |
| Dravenor Parte 3 | 3 |
| Gaia Vol. I | 99 |
| Gaia Vol. II | 46 |
| Fichas Sueltas | 11 |
| **Total** | **361** |
