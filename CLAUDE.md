# Catálogo interno de Dilan Home

App web de una sola página que muestra los productos de Dilan Home (precios, stock, fotos, estado en la tienda) y arma
presupuestos para compartir por WhatsApp. Se publica en GitHub Pages: https://dilanhomeok-sudo.github.io/dilan-catalogo/
Repo: `dilanhomeok-sudo/dilan-catalogo`, rama `master`. Idioma de la app y de las respuestas: español rioplatense (voseo).

## Estructura
- `index.html`: **toda la app** (HTML + CSS + JS vanilla, sin build ni dependencias). Es lo que se publica.
- `catalogo.html`: versión vieja, no se usa. No tocar.
- `tiendanube.json`: mapa SKU → link de la tienda online. **Lo genera un script, no se edita a mano.**
- `tools/generar_tiendanube.py`: lee el listado público de dilan.com.ar (`/productos/?page=N`, 12 por página) y arma el JSON.
- `.github/workflows/tiendanube.yml`: corre el script todos los días a las 10:00 UTC (07:00 Argentina) y guarda el JSON.
- `logo.webp`, `.nojekyll`.

## De dónde salen los datos (todo se lee en el navegador, no hay servidor propio)
| Dato | Fuente | Cómo se actualiza |
|---|---|---|
| Productos, precio, stock, rubros | Google Sheet publicado como CSV (`CSV_URL`) | Una tarea programada en **otra PC** exporta de Contabilium (por navegador, no hay API) y sube el archivo a Drive. |
| Fecha del último cambio de precio y foto (`Imagen`) | Otra planilla publicada (`FECHAS_URL`, "Ultima_Actualizacion_Precios") | La genera la skill `actualizar-fechas-precios`. Las fotos nuevas no aparecen hasta que corra. |
| "Última carga de Contabilium" | Apps Script (`ESTADO_URL`) que devuelve la fecha de modificación del archivo `_tmp_Productos_36827_*.xlsm` de Drive | Automático: cada vez que la tarea sube el archivo. |
| Publicado en la tienda online | `tiendanube.json` | Acción diaria de GitHub. |
| Fotos | `app.contabilium.com/files/explorer/36827/Productos-Servicios/concepto-<Imagen>`, redimensionadas por wsrv.nl | Si cambian la foto con el mismo nombre, puede tardar por la caché de wsrv.nl. |

Las columnas del CSV se leen por posición (`COL_SKU=1, COL_NAME=3, COL_BAR=8, COL_PRICE=16, COL_STOCK=20, COL_RUBRO=23, COL_SUB=24`).
Si Contabilium cambia el orden de columnas del export, hay que ajustar esas constantes.

## Reglas de negocio (no cambiar sin que lo pida Dilan)
- **El precio de la planilla es el de EFECTIVO** (efectivo, débito o transferencia).
- **Precio de lista = lista Ahoramis = efectivo × 1,20.** Se muestra primero y en **naranja**; el efectivo va al lado en **verde**.
- Listas (`LISTAS` en `index.html`): 3 Cuotas Simple +10 % · MyPime 6 +20 % · Ahoramis +20 % · Naranja +25 % · BNA/Santander +30 %.
- **Los porcentajes de recargo no se muestran en pantalla** (los ve el cliente). Solo viven en el código (`pct`).
- Cuotas por lista (`c`, con `d` = por defecto): Ahoramis 3/6/12/15 (6) · BNA 3/6/12/18/20 (20) · Naranja 5/10 (10) · MyPime 6 · Simple 3.
  El recargo es el mismo para cualquier cantidad de cuotas de la lista. **Esto es un supuesto que Dilan no confirmó del todo.**
- Los precios se redondean a pesos enteros por unidad (`unit()`), y el total es la suma de unidades redondeadas.
- El estado "En la web" se calcula por SKU contra `tiendanube.json`. Si el JSON no carga, no se muestra nada (nunca "no publicado" sin saberlo).

## Qué hace la app
Búsqueda por nombre/SKU/código de barras · filtros rubro, sub-rubro, stock, tienda web y antigüedad del precio · detalle del producto
(precios, cantidad, listas, stock, estado en la tienda con link) · **presupuesto** (carrito en `localStorage`, clave `dh_presupuesto_v1`, con
lista de precios elegible, cantidades, total y simulador de cuotas) · **WhatsApp**: arma una imagen (canvas) con fotos, total y cuotas;
en celular usa el menú de compartir, en computadora copia la imagen y abre WhatsApp con el texto (se pega con Ctrl+V) ·
**Vaciar** confirma en el mismo botón (no usar `confirm()`, a veces no se muestra) · fecha de última carga bajo "Actualizar".

## Límites conocidos
- **No se puede importar de Contabilium desde la app**: no hay API y el export necesita sesión en navegador. El botón Actualizar solo
  vuelve a leer la planilla. Un día sin carga se marca en naranja (más de 30 h).
- El conector de Tiendanube no devuelve SKU y arma links con otro dominio: por eso se usa el listado público de la tienda.
- Hay SKU en la tienda que no están en la planilla (unos 243 al 18/10/2026) y ~300 productos sin foto asignada.
- La imagen de WhatsApp solo incluye fotos que el navegador pueda leer desde wsrv.nl (CORS); si una falla, queda el recuadro gris.

## Cómo probar localmente
1. `cd` a esta carpeta y correr `py -m http.server 8765` (en esta PC `python` no anda, es `py`).
2. Abrir `http://localhost:8765/index.html`. **No abrir el archivo directo (`file://`)**: así no carga la planilla.
3. Verificar en ancho de escritorio y de celular (375 px), y que no haya errores en la consola.
4. El panel del navegador a veces abre una pestaña `file://` al editar: cerrarla y usar la de `localhost`.
5. Si la primera carga se queda en "Cargando productos" en el navegador de pruebas, llamar `loadData()` desde la consola.

## Cómo publicar
- Mostrarle el cambio a Dilan **antes** de publicar y esperar su OK.
- Publicar = `git add` + `git commit` + `git push origin master`. GitHub Pages tarda ~1 minuto; verificar con `curl` que el sitio sirve lo nuevo.
- Los mensajes de commit en español, con el trailer de coautoría que indique la sesión.
- No guardar claves ni tokens en el repo (es público).

## Estilo
Lista limpia y sobria: lo nuevo debe ser discreto (ver "En la web"). Colores: naranja = precio de lista, verde = efectivo, teal = acciones,
marrón = botones principales. Probar siempre en celular. Accesibilidad: botones con `aria-label`, foco visible, Escape cierra paneles.
