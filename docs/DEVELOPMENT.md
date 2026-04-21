# Documentación técnica — Animu Exxet

## Arquitectura

El módulo tiene dos capas:

**Offline (Python)** — `tools/`
- `generate_bestiary.py`: extrae stat blocks de markdowns y genera los compendios de criaturas
- `generate_artifacts.py`: extrae artefactos de Prometheum y genera el compendio de artefactos
- `extract_prometheum.py`: re-extrae el PDF de Prometheum respetando columnas
- `import_excel.py`: convierte fichas Excel a JSON de animabf (uso offline)

**Online (JavaScript)** — `scripts/`
- `module.js`: punto de entrada, registra hooks y botones
- `services/compendium-service.js`: importador de datasets a compendios de mundo
- `services/bulk-import.js`: diálogo de importación múltiple de Excel
- `services/excel-import.js`: parser de Excel a actor animabf

---

## Compendios

### Creatures Exxet (`packs/creatures-exxet`)

LevelDB con actores de tipo `character`. Estructura de carpetas:

```
Creatures Exxet/
  [Fuente 1]/
  [Fuente 2]/
    [Región A]/   ← solo en fuentes con datos geográficos
    [Región B]/
  ...
```

Cada actor incluye:
- Sistema completo de animabf (atributos, resistencias, combate, magia, psíquico, dominé)
- Items embebidos: armas naturales (tipo `weapon`) y armaduras (tipo `armor`)
- Notas con ventajas, poderes, Ki, técnicas y otros campos no estructurados
- Token con tamaño según Tamaño del ser y visión según Percepción × 20m

### Artifacts Exxet (`packs/artifacts-exxet`)

LevelDB con items de tipo `weapon`, `armor` y `note`. Estructura:

```
Artifacts Exxet/
  Armas/
  Armaduras/
  Artefactos y Notas/
```

---

## Importador de Excel

### Campos importados desde la hoja `Resumen`

| Campo | Celdas | Método |
|---|---|---|
| Nombre | M3 | Fijo |
| Nivel | F11 | Fijo |
| Clase / Raza | L11 | Fijo |
| PV | E12 | Fijo |
| Categoría | L12 | Fijo |
| Atributos (8) | F13-R14 | Fijo |
| Presencia | H15 | Fijo |
| Resistencias (5) | F16-V16 | Fijo |
| Turno / Ataque / Defensa / Daño | H19-H28 | Fijo |
| TA (7 tipos) | H32-AF32 | Fijo |
| ACT | Busca "ACT:" | Dinámico |
| Zeón | Busca "Zeón:" | Dinámico |
| Reg. Zeón | Busca "Reg. Zeon:" | Dinámico |
| Proyección Mágica (off/def) | Busca "Proyección Mágica:" | Dinámico |
| Nivel de Magia (vías) | Busca "Nivel de Magia:" | Dinámico |
| Convocar / Dominar / Atar / Desconvocar | Busca labels | Dinámico |
| Potencial Psíquico | Busca "Potencial Psíquico:" | Dinámico |
| Proyección Psíquica (off/def) | Busca "Proyección Psíquica:" | Dinámico |
| CV Libres / Innatos | Busca "CV Libres:" | Dinámico |
| Disciplinas / Poderes Psíquicos | Busca labels | Dinámico |
| Puntos de Ki | Busca "Puntos de Ki:" | Dinámico |
| Acumulaciones Ki (6 stats) | Busca "Acumulaciones:" | Dinámico |
| Habilidades de Ki | Busca "Habilidades de Ki:" | Dinámico |
| Técnicas | Busca "Técnicas:" | Dinámico |
| Tamaño / Movimiento | Busca labels | Dinámico |
| Cansancio / Regeneración | Busca labels | Dinámico |
| Habilidades secundarias | Busca "Habilidades secundarias:" | Dinámico |
| Ventajas / Poderes / Especial | Busca labels | Dinámico |
| Lenguas | Busca "Lenguas:" | Dinámico |

### Campos importados desde la hoja `Combate`

- Piezas de armadura individuales (rows 12-15) con TA por tipo
- Llevar Armadura (requisito) y Penalizador Natural
- Armas equipadas (hasta 10 slots) con daño, turno, críticos, entereza, rotura, presencia, calidad
- Artes Marciales como arma si tiene datos

### Campos importados desde la hoja `Ki`

- Conocimiento Marcial total y usado

### Notas generadas

Cuando hay múltiples armas, se generan notas con el texto completo de:
- Turno, Ataque, Defensa, Daño

---

## Generación de compendios (offline)

### Requisitos

```bash
pip install openpyxl plyvel pymupdf
```

### Regenerar Creatures Exxet

```bash
cd tools/
python3 generate_bestiary.py
```

Los markdowns fuente deben estar en `/animu/data/docs_md/`.

### Regenerar Artifacts Exxet

```bash
# Primero re-extraer el PDF con respeto de columnas
python3 extract_prometheum.py

# Luego generar el compendio
python3 generate_artifacts.py
```

### Importar fichas Excel (offline)

```bash
python3 tools/import_excel.py ficha1.xlsm ficha2.xlsm -o output/
```

Genera JSONs que se pueden importar manualmente en Foundry.

---

## Compatibilidad

- Foundry VTT: v13+
- Sistema animabf: v2.2.1+
- Excel: cualquier versión con hoja `Resumen` (no requiere `NamedRangesList`)
