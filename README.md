# PasteScribe

Escribe un texto pegado **letra por letra**, como si lo teclearas tú. Hay dos versiones:

| | Dónde escribe | Carpeta |
|---|---|---|
| **App de escritorio** | En cualquier programa, ventana o formulario del equipo que tenga el foco | [`desktop-app/`](desktop-app) |
| **Extensión de Chrome** | Solo en la pestaña abierta en ese momento en el navegador | [`chrome-extension/`](chrome-extension) |

## App de escritorio (Windows, macOS, Linux/X11)

Requisitos: Python 3.9+ con `tkinter` y `pynput`.

```bash
cd desktop-app
python -m pip install -r requirements.txt
python pastescribe.py
```

En Windows también puedes hacer doble clic en `iniciar_windows.bat`, que instala las dependencias y abre la app.

1. Pega el texto en la ventana (Ctrl+V / Cmd+V o «Pegar del portapapeles»).
2. Ajusta la pausa entre letras, la cuenta atrás y si quieres «ritmo humano».
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
2. Abre la extensión, pega el texto, ajusta la velocidad y pulsa **Escribir**. El popup se cierra y la escritura empieza.
3. Si no había ningún campo enfocado, la extensión espera (hasta 60 s) a que hagas clic en uno.
4. **Esc** en la página, el botón *Detener* del aviso en pantalla o *Detener* en el popup lo paran. Si el campo pierde el foco, la escritura se detiene para no escribir donde no debe.

Privacidad: solo actúa en la pestaña activa cuando pulsas el icono (permiso `activeTab`), no envía nada a ningún servidor y el texto solo se guarda en la sesión del navegador. Permisos: `activeTab`, `scripting`, `storage`.

Limitaciones:
- No funciona en páginas internas (`chrome://…`, Chrome Web Store) ni en iframes de otro origen.
- Los editores que dibujan su propio texto (p. ej. Google Docs) no usan campos de texto estándar y pueden ignorarlo.
- En campos de una sola línea los saltos de línea se convierten en espacios.

## Pruebas

```bash
cd desktop-app && python -m unittest discover -s tests     # motor de escritura
npm i playwright && node chrome-extension/tests/content.test.js   # script de contenido en Chromium
```

`python tools/make_icons.py` regenera los iconos de la extensión.
