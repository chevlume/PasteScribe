# PasteScribe

🇬🇧 [English](README.md) · 🇪🇸 Español

Escribe un texto pegado **letra por letra**, como si lo teclearas tú. Hay dos versiones:

| | Dónde escribe | Carpeta |
|---|---|---|
| **App de escritorio** | En cualquier programa, ventana o formulario del equipo que tenga el foco | [`desktop-app/`](desktop-app) |
| **Extensión de Chrome** | Solo en la pestaña abierta en ese momento en el navegador | [`chrome-extension/`](chrome-extension) |

## App de escritorio (Windows, macOS, Linux/X11)

La interfaz sale **en inglés por defecto**; cámbiala a español con el selector *Idioma* de la ventana (se recuerda).

### Windows: un único `.exe`, sin ventana de consola

Compílalo una vez en tu PC con Windows (necesita Python 3.9+ instalado):

1. Haz doble clic en **`desktop-app\build_windows.bat`**. Instala lo necesario, compila y comprueba la app.
2. Coge **`desktop-app\dist\PasteScribe.exe`** y cópialo donde quieras (por ejemplo, el escritorio). Doble clic: se abre **sin ventana de consola**.

¿Sin un PC con Windows a mano? En GitHub, pestaña *Actions* → *Build Windows exe* → *Run workflow*, y descarga `PasteScribe-windows` desde *Artifacts* de la ejecución.

Ojo: el `.exe` no está firmado digitalmente, así que Windows SmartScreen puede mostrar «Windows protegió su PC» (pulsa *Más información* → *Ejecutar de todas formas*), y algunos antivirus marcan como sospechoso cualquier programa que teclea por ti (falso positivo). Si ocurre un error, los detalles se guardan en `%USERPROFILE%\.pastescribe.log`.

### Ejecutar desde el código (cualquier sistema)

Requisitos: Python 3.9+ con `tkinter` y `pynput`.

```bash
cd desktop-app
python -m pip install -r requirements.txt
python pastescribe.py
```

En Windows también puedes hacer doble clic en `iniciar_windows.bat`, que instala las dependencias y abre la app (sin dejar una consola abierta).

### Uso

1. Pega el texto en la ventana (Ctrl+V / Cmd+V o *Pegar del portapapeles*).
2. Ajusta la pausa entre letras, la cuenta atrás y si quieres pausas irregulares (variación aleatoria).
3. Pulsa **Iniciar** y, durante la cuenta atrás, **haz clic en el campo de destino** (en cualquier aplicación).
4. Empieza a escribir. **Esc** (en todo el sistema) o el botón *Detener* lo paran al instante.

Seguridad:
- **Saltos de línea** (opción por defecto: *Convertir en espacio*): pulsar Enter en un cuadro de búsqueda o en un formulario lo envía y rompe la escritura. Elige *Pulsar Enter* solo para campos de varias líneas (editores, `textarea`).
- Si cambias de ventana mientras escribe (Alt+Tab, otra ventana que toma el foco), la escritura se detiene sola (solo Windows).
- En Windows, Esc se detecta consultando el teclado, sin interceptar la entrada del sistema.
- Si algo se descontrola: Esc; si no responde, cierra la app desde el Administrador de tareas (Ctrl+Mayús+Esc).

Notas:
- **macOS**: concede a la terminal/Python permisos de *Accesibilidad* y *Supervisión de entrada* (Ajustes del Sistema → Privacidad y seguridad), si no, el sistema ignora las teclas.
- **Linux**: funciona en X11. En Wayland los programas no pueden inyectar teclas en otras ventanas; usa una sesión Xorg.
- Los tabuladores se escriben como Tab (en un formulario web, Tab cambia de campo) y, con *Pulsar Enter*, en un editor de código el autosangrado puede añadir espacios extra.
- La pausa mínima entre letras es de 10 ms (5 ms en la extensión). Sin pausa, el sistema recibe miles de teclas de golpe: el texto aparece "en bloque", el programa de destino sigue escribiendo cuando PasteScribe ya terminó y Esc no puede detenerlo.
- En Linux, si escribes muchos caracteres exóticos a la vez, usa una pausa de **30 ms o más** (por defecto 60 ms).

## Extensión de Chrome (Manifest V3)

Instalación (modo desarrollador):

1. Abre `chrome://extensions` y activa **Modo de desarrollador**.
2. **Cargar descomprimida** → elige la carpeta `chrome-extension/`.

Uso:

1. Haz clic en el campo de la página donde quieras escribir (cuadro de texto, `textarea`, campo de contraseña o editor `contenteditable`).
2. Abre la extensión, pega el texto, ajusta la velocidad y pulsa **Escribir** (la interfaz sale en inglés por defecto; cámbiala a español con el selector del panel, y se recuerda). El popup se cierra y la escritura empieza.
3. Si no había ningún campo enfocado, la extensión espera (hasta 60 s) a que hagas clic en uno.
4. **Esc** en la página, el botón *Detener* del aviso en pantalla o *Detener* en el popup lo paran. Si el campo pierde el foco, la escritura se detiene para no escribir donde no debe.

Privacidad: solo actúa en la pestaña activa cuando pulsas el icono (permiso `activeTab`), no envía nada a ningún servidor y el texto solo se guarda en la sesión del navegador. Permisos: `activeTab`, `scripting`, `storage`.

Limitaciones:
- No funciona en páginas internas (`chrome://…`, Chrome Web Store) ni en iframes de otro origen.
- Los editores que dibujan su propio texto (p. ej. Google Docs) no usan campos de texto estándar y pueden ignorarlo.
- En campos de una sola línea los saltos de línea se convierten en espacios.
- Los editores Draft.js (como el cuadro de publicar de X) reciben cada carácter como un evento de pegado en lugar de escritura normal, porque se rompen si el navegador edita su texto directamente. Está probado contra un editor Draft.js real en local, no contra x.com. Si una web falla, la app de escritorio funciona en todas partes.

## Publicar en la Chrome Web Store

Todo el material está preparado; falta tu cuenta de desarrollador. Los textos de la ficha, los permisos justificados y los datos de privacidad están en [`CHROMEWEBSTORE.md`](CHROMEWEBSTORE.md).

1. Rellena tu correo en [`docs/privacy-policy.md`](docs/privacy-policy.md) (español) y [`docs/privacy-policy.en.md`](docs/privacy-policy.en.md) (inglés) y publícalas en una **URL pública** (por ejemplo, ese mismo archivo en GitHub si el repositorio es público, o un Gist público).
2. Crea el paquete: `tools/package_extension.sh` (genera `dist/pastescribe-v<versión>.zip`). Sin Bash, comprime **el contenido** de `chrome-extension/` (que `manifest.json` quede en la raíz del ZIP).
3. Entra en el [Panel para desarrolladores](https://chrome.google.com/webstore/devconsole), acepta el contrato y paga la cuota única de registro (5 USD).
4. *Nuevo elemento* → sube el ZIP → completa *Ficha de Play Store*, *Privacidad* y *Distribución* con lo que indica `CHROMEWEBSTORE.md`. Imágenes en `store-assets/en/` y `store-assets/es/` (se regeneran con `LANG_UI=en node tools/make_store_assets.js`). La extensión está traducida al inglés (por defecto) y al español: el panel tiene un selector EN/ES.
5. *Enviar para revisión*. La primera revisión suele tardar de 1 a 3 días laborables.

Para cada actualización: sube `version` en `chrome-extension/manifest.json`, vuelve a crear el ZIP y súbelo como nueva versión.

## Pruebas

```bash
cd desktop-app && python -m unittest discover -s tests     # motor de escritura, traducciones, lógica de la ventana
xvfb-run -a python tests/gui_real_test.py                  # la ventana real (necesita tkinter y un servidor X; Linux)
npm i playwright && LANG_UI=es node tests/extension/content.test.js && LANG_UI=en node tests/extension/content.test.js   # script de contenido en Chromium
```

Test de regresión con un editor Draft.js (el cuadro de publicar de X usa Draft.js): `cd tests/extension/draft && npm install && npm test`.

`python tools/make_icons.py` regenera los iconos de la extensión.
