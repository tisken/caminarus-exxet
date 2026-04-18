# Animu Exxet

Addon para Foundry VTT orientado al sistema `animabf` que importa fichas de criaturas desde:

- `Anima Beyond Fantasy - Core Exxet`
- `Anima Beyond Fantasy - Los que caminaron con nosotros`

El proyecto no empaqueta compendios binarios. En su lugar incluye JSON generados a partir de los manuales y una utilidad dentro de Foundry para crear o recrear compendios de mundo con esos actores.

## Qué hace ahora

- Genera documentos de actor compatibles con `animabf`.
- Crea compendios de mundo separados por libro.
- Conserva el bloque original extraído y metadatos de fuente dentro de cada ficha.
- Intenta mapear automáticamente atributos, resistencias, iniciativa, vida, movimiento, regeneración, habilidades secundarias y parte de lo sobrenatural.

## Qué no hace todavía

- No convierte todos los ataques naturales en armas embebidas.
- No enlaza técnicas, conjuros o poderes psíquicos con ítems oficiales.
- No corrige manualmente todos los artefactos OCR de los nombres variantes.

## Uso en Foundry

1. Copia la carpeta `animu-exxet` dentro de `Data/modules/`.
2. Asegúrate de tener instalado y activado el sistema `Anima Beyond Fantasy` (`animabf`).
3. Activa el módulo `Animu Exxet` en tu mundo.
4. Abre el directorio de compendios y pulsa `Animu Exxet`, o entra en la configuración del módulo.
5. Importa uno o ambos bestiarios.

## Regenerar los datos

El generador usa Python estándar, sin dependencias externas.

```bash
python3 tools/generate_bestiary.py \
  --core "/ruta/a/Anima Beyond Fantasy - Core Exxet.md" \
  --walking "/ruta/a/Anima Beyond Fantasy - Los que caminaron con nosotros_unlocked.md"
```

Si estás trabajando dentro del entorno de desarrollo original de este proyecto, el script intenta descubrir esos ficheros automáticamente.

## Estructura

- `data/generated/`: datasets listos para importar.
- `data/reference/animabf-template.json`: plantilla de datos del sistema fuente.
- `scripts/`: lógica del módulo dentro de Foundry.
- `templates/`: interfaz Handlebars del importador.
- `tools/`: utilidades de generación y mantenimiento.
- `docs/roadmap.md`: mejoras siguientes sugeridas.
