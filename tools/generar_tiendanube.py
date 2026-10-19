#!/usr/bin/env python3
"""Genera tiendanube.json: qué SKU están publicados en la tienda (dilan.com.ar) y el link de cada producto.

Lee el listado público de la tienda (/productos/?page=N). Cada producto del listado trae su link y los SKU de sus
variantes. No necesita claves ni sesión. El catálogo lee el resultado para mostrar "Publicado en la tienda".

Uso:  python tools/generar_tiendanube.py [salida.json]
"""
import html
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

BASE = "https://dilan.com.ar/productos/"
UA = "Mozilla/5.0 (compatible; DilanCatalogo/1.0)"
MAX_PAGINAS = 200          # tope de seguridad
PAUSA = 0.4                # segundos entre páginas, para no cargar la tienda


def bajar(url, intentos=3):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", "ignore")
        except Exception as e:
            if i == intentos - 1:
                raise
            time.sleep(2 * (i + 1))


def productos_de(pagina):
    """Devuelve [(url, [skus])] de cada producto del listado.

    Cada producto trae sus datos en dos lugares: el JSON-LD (sku + link) y, si tiene variantes, data-variants.
    Se usan los dos para no perder ninguno."""
    bloques = re.split(r'(?=class="js-item-product)', pagina)[1:]
    out = []
    for b in bloques:
        skus, url = [], None
        for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', b, re.S):
            try:
                j = json.loads(m.group(1))
            except ValueError:
                continue
            if isinstance(j, dict) and j.get("@type") == "Product":
                if j.get("sku"):
                    skus.append(str(j["sku"]))
                url = url or (j.get("mainEntityOfPage") or {}).get("@id")
        var = re.search(r'data-variants="([^"]*)"', b)
        if var:
            skus += re.findall(r'"sku":"([^"]+)"', html.unescape(var.group(1)))
        if not url:
            link = re.search(r'href="(https://dilan\.com\.ar/productos/[^"?#]+/?)"', b)
            url = link.group(1) if link else None
        skus = [x.strip() for x in dict.fromkeys(skus) if x.strip()]
        if url and skus:
            out.append((url, skus))
    return out


def main(destino):
    mapa = {}
    vistos_urls = set()
    for n in range(1, MAX_PAGINAS + 1):
        pagina = bajar(f"{BASE}?page={n}")
        items = productos_de(pagina)
        nuevos = [(u, s) for u, s in items if u not in vistos_urls]
        print(f"página {n}: {len(items)} productos, {len(nuevos)} nuevos", flush=True)
        if not nuevos:
            break
        for u, skus in nuevos:
            vistos_urls.add(u)
            for s in skus:
                mapa[s.strip()] = u
        time.sleep(PAUSA)

    if len(mapa) < 100:       # algo cambió en la tienda: no pisar el archivo bueno con uno casi vacío
        sys.exit(f"Solo se encontraron {len(mapa)} SKU; no se guarda el archivo.")

    salida = {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "productos": dict(sorted(mapa.items())),
    }
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Listo: {len(mapa)} SKU en {len(vistos_urls)} productos -> {destino}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "tiendanube.json")
