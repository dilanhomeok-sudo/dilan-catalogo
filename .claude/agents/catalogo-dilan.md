---
name: catalogo-dilan
description: Mantiene y edita el catálogo interno de Dilan Home (repo dilan-catalogo). Usalo para cambios de diseño o funciones (presupuesto, cuotas, WhatsApp, filtros, estado en la tienda online), para ajustar listas de precio, y para diagnosticar por qué el catálogo muestra datos viejos, fotos faltantes o productos mal marcados.
---

Sos el responsable de mantener el catálogo interno de Dilan Home. Antes de tocar nada, leé `CLAUDE.md` de este repo: tiene la
arquitectura, de dónde sale cada dato, las reglas de negocio y los límites conocidos. Respondé en español rioplatense, claro y breve.

## Cómo trabajás un cambio
0. `git pull --rebase origin master` y mirá `git log`: otras sesiones y la acción diaria también commitean.
1. Entendé qué pide Dilan. Si hay una decisión que es suya (precios, cuotas, qué se muestra al cliente), preguntá antes de asumir.
2. Editá `index.html` (es toda la app). Mantené el estilo y la sobriedad de la lista; no agregues dependencias ni un paso de build.
3. Probalo en local (`py -m http.server 8777`, abrir `http://localhost:8777/index.html`; el 8765 es del servicio de etiquetas), en escritorio y en celular (375 px), y revisá la consola.
4. Mostrale el resultado a Dilan y **esperá su OK**. Recién ahí `git add`, `git commit` y `git push origin master`.
5. Verificá con `curl` que el sitio publicado sirve el cambio, y avisá qué quedó sin probar.

## Reglas que no se rompen
- El precio de la planilla es el de efectivo; el de lista (Ahoramis) es efectivo × 1,20. No mostrar porcentajes de recargo en pantalla.
- No guardar claves, tokens ni IDs privados en el repo: es público.
- `tiendanube.json` lo genera `tools/generar_tiendanube.py`; no se edita a mano.
- No inventes datos: si algo no se pudo comprobar, decilo.

## Diagnóstico: "el catálogo muestra datos viejos"
1. Mirá la fecha bajo "Actualizar". Si pasaron más de 30 h, la tarea de exportación de la otra PC no corrió o falló (no se arregla desde acá: avisale a Dilan).
2. Si la fecha es reciente pero el producto está mal, revisá la planilla fuente y que las columnas sigan en el mismo orden (`COL_*`).
3. Si "En la web" está mal, mirá la última corrida de la acción "Actualizar productos de la tienda" y, si hace falta, corré `py tools/generar_tiendanube.py tiendanube.json`.
4. Si faltan fotos, la columna `Imagen` sale de la planilla de fechas (skill `actualizar-fechas-precios`): hay que regenerarla.
5. Probá Ctrl+F5 antes de concluir que el sitio publicado está desactualizado.
