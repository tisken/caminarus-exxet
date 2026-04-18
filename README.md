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

El proyecto no empaqueta compendios binarios. En su lugar incluye JSON generados a partir de los manuales y una utilidad dentro de Foundry para crear o recrear compendios de mundo con esos actores.

## Qué hace ahora

- Genera documentos de actor compatibles con `animabf`.
- Crea compendios de mundo separados por libro.
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
3. Abre el importador del módulo desde Foundry.
4. Importa uno o varios libros; cada fuente se crea como compendio de mundo independiente.

## Regenerar los datos

El generador usa Python estándar, sin dependencias externas.

```bash
python3 tools/generate_bestiary.py \
  --core "/ruta/a/Anima Beyond Fantasy - Core Exxet.md" \
  --walking "/ruta/a/Anima Beyond Fantasy - Los que caminaron con nosotros_unlocked.md"
```

Si estás trabajando dentro del entorno de desarrollo original de este proyecto, el script intenta descubrir esos ficheros automáticamente.

Tras regenerar los datos, conviene volver a empaquetar `dist/animu-exxet.zip`, ya que es el artefacto que usa Foundry para instalar o actualizar el módulo desde el manifest.

## Estructura

- `data/generated/`: datasets listos para importar.
- `data/reference/animabf-template.json`: plantilla de datos del sistema fuente.
- `scripts/`: lógica del módulo dentro de Foundry.
- `templates/`: interfaz Handlebars del importador.
- `tools/`: utilidades de generación y mantenimiento.
- `docs/roadmap.md`: mejoras siguientes sugeridas.
