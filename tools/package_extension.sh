#!/usr/bin/env bash
# Crea el ZIP de la extensión listo para subir a la Chrome Web Store.
# Uso: tools/package_extension.sh   ->  dist/pastescribe-v<versión>.zip
set -euo pipefail
cd "$(dirname "$0")/../chrome-extension"

VERSION=$(python3 -c "import json;print(json.load(open('manifest.json'))['version'])")
OUT="../dist/pastescribe-v${VERSION}.zip"
mkdir -p ../dist
rm -f "$OUT"

# Solo lo que Chrome necesita: sin tests ni archivos de desarrollo.
zip -r -q "$OUT" manifest.json content.js popup icons \
  -x "*.DS_Store" -x "*Thumbs.db"

echo "Creado: $OUT ($(du -h "$OUT" | cut -f1))"
unzip -l "$OUT"
