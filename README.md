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

El proyecto crea automáticamente un compendio de mundo llamado `Creatures Exxet`, con una carpeta interna por manual, y además incluye JSON generados a partir de los manuales para poder copiar esas fichas a compendios de mundo si hace falta.

## Qué hace ahora

- Genera documentos de actor compatibles con `animabf`.
- Crea automáticamente el compendio de mundo `Creatures Exxet` con subcarpetas por libro al activar el addon siendo GM.
- Permite copiar esas fichas a compendios de mundo independientes desde el importador.
- Conserva el bloque original extraído y metadatos de fuente dentro de cada ficha.
- Intenta mapear automáticamente atributos, resistencias, iniciativa, vida, movimiento, regeneración, habilidades secundarias y parte de lo sobrenatural.
- Coloca ventajas, técnicas, Ki, invocaciones, poderes y otros campos no estructurados en las notas internas de `animabf`.

## Qué no hace todavía

- No convierte todos los ataques naturales en armas embebidas.
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
3. En la primera carga con un GM, el módulo prepara automáticamente el compendio `Creatures Exxet`.
4. Dentro verás una carpeta por manual y, dentro de cada una, sus criaturas.
5. Si quieres versiones de mundo editables o reconstruibles, abre el importador del módulo y copia allí uno o varios libros.

## Estructura

- `data/generated/`: datasets JSON listos para importar a compendios de mundo.
- `data/reference/animabf-template.json`: plantilla de datos del sistema fuente.
- `packs/`: exportación JSON del compendio generado, útil como referencia y verificación.
- `scripts/`: lógica del módulo dentro de Foundry.
- `templates/`: interfaz Handlebars del importador.
- `tools/`: utilidades de generación y mantenimiento.
- `docs/roadmap.md`: mejoras siguientes sugeridas.
