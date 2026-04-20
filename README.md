# Animu Exxet

Addon para Foundry VTT orientado al sistema `animabf` que importa fichas de criaturas y PNJ desde:

- `Anima Beyond Fantasy - Core Exxet`
- `Anima Beyond Fantasy - Los que caminaron con nosotros`
- `ABF Complemento Web Vol. 1`
- `Anima Gate of Memories - Guía del Mundo Perfecto`
- `Dramatis Personae`
- `Dramatis Personae Vol. 2`
- `Anima Pantalla del Director`
- `DRAVENOR Ejército regular de La Máquina` partes `1`, `2` y `3`
- `Anima Beyond Fantasy - Gaia Volumen I`
- `Anima Beyond Fantasy - Gaia Volumen II`
- `Fichas sueltas` (Etheldrea, Jigoku, Orochi, Stravos, Pazusu)

El proyecto genera **361 fichas** con atributos, resistencias, habilidades secundarias, armas naturales y armaduras embebidas, organizadas en un compendio `Creatures Exxet` con una carpeta por manual.

## Qué hace

- Genera documentos de actor compatibles con `animabf` con la estructura real del sistema (verificada contra las fichas oficiales del Caballo y ABF-Compendiums).
- Incluye el compendio estático `Creatures Exxet` con subcarpetas por libro.
- Permite copiar fichas a compendios de mundo independientes desde el importador.
- Mapea automáticamente atributos primarios (con modificador), resistencias, iniciativa, vida, movimiento, regeneración, habilidades secundarias y parte de lo sobrenatural.
- Genera **518 armas naturales** embebidas con daño base y tipo de crítico.
- Genera **144 armaduras naturales** embebidas con valores de TA por tipo de daño.
- Coloca ventajas, técnicas, Ki, invocaciones, poderes y otros campos no estructurados en las notas internas de `animabf`.

## Qué no hace todavía

- No enlaza técnicas, conjuros o poderes psíquicos con ítems oficiales.
- No corrige manualmente todos los artefactos OCR de los nombres variantes.

## Instalación en Foundry

Instala primero el sistema base:

- Sistema `animabf`: `https://raw.githubusercontent.com/AnimaBeyondDevelop/AnimaBeyondFoundry/main/src/system.json`

Después instala el addon con esta `Manifest URL`:

- Módulo `animu-exxet`: `https://raw.githubusercontent.com/tisken/caminarus-exxet/main/module.json`

## Uso en Foundry

1. Asegúrate de tener instalado y activado el sistema `Anima Beyond Fantasy` (`animabf`).
2. Activa el módulo `Animu Exxet` en tu mundo.
3. El compendio `Creatures Exxet` aparecerá directamente en la lista de compendios con todas las criaturas organizadas por manual.
4. Si quieres versiones de mundo editables, abre el importador del módulo y copia allí uno o varios libros.

## Estructura

- `data/generated/`: datasets JSON listos para importar a compendios de mundo.
- `data/reference/animabf-template.json`: plantilla de datos del sistema fuente.
- `packs/`: compendio estático con los actores generados.
- `scripts/`: lógica del módulo dentro de Foundry.
- `templates/`: interfaz Handlebars del importador.
- `tools/`: utilidades de generación y mantenimiento.
