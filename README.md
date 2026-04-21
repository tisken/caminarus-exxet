# Animu Exxet

Addon para Foundry VTT orientado al sistema `animabf` que incluye compendios de criaturas, artefactos y un importador de fichas Excel.

> **Aviso legal:** Este módulo es un proyecto personal gratuito, desarrollado a partir de manuales físicos en posesión del autor. No distribuye ni reproduce contenido con derechos de autor. Todos los nombres, personajes, criaturas y contenido de Anima Beyond Fantasy son © 2005 – 2026 Anima Project. Todos los derechos reservados. Este módulo no está afiliado ni respaldado por Anima Project.
>
> Sitio oficial: [animaproject.studio](https://www.animaproject.studio/juego-de-rol/)

## Instalación

Instala primero el sistema base:

- Sistema `animabf`: `https://raw.githubusercontent.com/AnimaBeyondDevelop/AnimaBeyondFoundry/main/src/system.json`

Después instala el addon:

- Módulo `animu-exxet`: `https://raw.githubusercontent.com/tisken/caminarus-exxet/main/module.json`

## Compendios incluidos

### Creatures Exxet
Más de **360 fichas** de criaturas y PNJ organizadas por fuente, con subcarpetas por región geográfica donde aplica. Cada ficha incluye:
- Atributos, resistencias, iniciativa, vida, movimiento y regeneración
- Habilidades secundarias
- Armas naturales embebidas con daño y tipo de crítico
- Armaduras naturales con valores de TA
- Tabs de místico, psíquico y dominé activados según corresponda
- Visión del token basada en Percepción

### Artifacts Exxet
Más de **100 artefactos** clasificados en Armas, Armaduras y Artefactos Varios, con stats de combate y descripción de poderes.

## Importador de fichas Excel (Multiimport)

Botón **"Multiimport fichas Excel"** en la pestaña de Actores. Permite importar fichas de personaje desde archivos `.xlsm` del Excel estándar de Anima Beyond Fantasy.

- Selección múltiple de archivos
- Compatible con cualquier versión del Excel que tenga la hoja `Resumen`
- Importa: atributos, resistencias, combate, armaduras, armas, magia, psíquico, Ki, habilidades secundarias, ventajas, técnicas y más
- Selector de carpeta de destino

## Uso

1. Activa el módulo en tu mundo con el sistema `animabf`.
2. Los compendios aparecen directamente en la lista de compendios.
3. Para importar fichas Excel: pestaña Actores → **"Multiimport fichas Excel"**.

## Estructura del proyecto

```
packs/          Compendios estáticos (LevelDB)
scripts/        Lógica del módulo en Foundry
tools/          Generadores Python (offline)
data/generated/ Datasets JSON de los compendios
images/         Carpetas para tokens y portraits
docs/           Documentación técnica
```
