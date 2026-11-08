# Chrome Web Store Listing — PasteScribe

> Last Updated: 2026-11-08
>
> La extensión está traducida: la interfaz sale **en inglés por defecto** y el usuario puede cambiarla a español con el selector EN/ES del panel (se recuerda). Textos en `chrome-extension/_locales/`. En el panel, la ficha base es el inglés y se añade el español desde el selector de idioma de «Ficha de Play Store» → «Añadir idioma».

## Store Listing — ESPAÑOL (traducción)

**Extension Name** [REQUIRED]
PasteScribe

**Short Description** [REQUIRED] (≤132 caracteres)
Escribe un texto pegado letra por letra en el campo de texto de la pestaña activa. Velocidad ajustable y parada con Esc.

**Detailed Description** [REQUIRED]
```
PasteScribe escribe, letra por letra, un texto que tú pegas en el campo de texto de la pestaña que tienes abierta.

FUNCIONES
• Escribe en cuadros de texto, áreas de texto, campos de contraseña y editores de texto enriquecido de la página
• Velocidad ajustable, de muy rápida a lenta
• Opción de pausas irregulares entre letras, con variación aleatoria
• Se detiene al instante con la tecla Esc o con el botón Detener
• Si el campo pierde el foco, deja de escribir para no teclear donde no debe
• Recuerda tu velocidad preferida
• Interfaz en inglés y español, con selector en el panel

CÓMO SE USA
1. Haz clic en el campo de texto de la página donde quieras escribir.
2. Abre PasteScribe desde la barra de herramientas y pega tu texto.
3. Elige la velocidad y pulsa «Escribir». El panel se cierra y empieza a escribir.
4. Si no había ningún campo seleccionado, espera a que hagas clic en uno.

PRIVACIDAD
PasteScribe no recopila ni envía ningún dato. No hace conexiones a internet. El texto que pegas solo se guarda en tu navegador durante la sesión y tus ajustes, en tu propio equipo.

PERMISOS
• «Leer y cambiar datos del sitio actual»: solo se usa en la pestaña activa, cuando pulsas el botón de la extensión, para escribir en el campo que has seleccionado. PasteScribe no lee el contenido de las páginas.

LIMITACIONES
No funciona en páginas internas de Chrome ni en la tienda de extensiones. Los editores que dibujan su propio texto (por ejemplo, algunos procesadores de texto en línea) pueden ignorarlo. En campos de una sola línea, los saltos de línea se convierten en espacios.

SOPORTE
¿Algún problema o sugerencia? Escríbenos a <TU_CORREO_DE_CONTACTO>.

Versión 1.3.0: ya disponible en español e inglés, con selector de idioma en el panel. Una velocidad mínima evita que el texto aparezca de golpe y permite detenerlo siempre con Esc.
```

**Category** [REQUIRED]
Productivity (Productividad)

**Single Purpose** [REQUIRED]
Escribe, letra por letra, un texto pegado por el usuario en el campo de texto enfocado de la pestaña activa.

**Primary Language** [REQUIRED]
English (la extensión usa `default_locale: en`); el español se añade como traducción

## Store Listing — ENGLISH (default language)

**Extension Name**
PasteScribe

**Short Description** (≤132 characters)
Types text you paste, letter by letter, into the text field of the active tab. Adjustable speed; stop anytime with Esc.

**Detailed Description**
```
PasteScribe types text that you paste, letter by letter, into the text field of the tab you have open.

FEATURES
• Types into text boxes, text areas, password fields and rich-text editors on the page
• Adjustable speed, from very fast to slow
• Optional irregular pauses between letters, with random variation
• Stops instantly with the Esc key or the Stop button
• If the field loses focus, it stops typing so it doesn't type where it shouldn't
• Remembers your preferred speed
• Interface in English and Spanish, with a language switch in the panel

HOW TO USE
1. Click the text field on the page where you want to type.
2. Open PasteScribe from the toolbar and paste your text.
3. Choose the speed and press "Type". The panel closes and typing begins.
4. If no field was selected, it waits until you click one.

PRIVACY
PasteScribe does not collect or send any data. It makes no internet connections. The text you paste is only kept in your browser for the current session, and your settings stay on your own computer.

PERMISSIONS
• "Read and change data on the current site": only used on the active tab, when you press the extension's button, to type into the field you selected. PasteScribe does not read the content of pages.

LIMITATIONS
It does not work on Chrome's internal pages or on the extension store. Editors that draw their own text (for example, some online word processors) may ignore it. In single-line fields, line breaks are turned into spaces.

SUPPORT
Found a problem or have a suggestion? Write to <YOUR_CONTACT_EMAIL>.

Version 1.3.0: now available in English and Spanish, with a language switch in the panel. A minimum typing speed prevents text from appearing all at once and lets you always stop with Esc.
```

**Category**
Productivity

**Single Purpose**
Types text pasted by the user, letter by letter, into the focused text field of the active tab.

**Primary Language**
English

### Permissions justification (English — for the review team)

| Permission | Justification |
|------------|---------------|
| activeTab | Grants temporary access only to the current tab when the user clicks the extension icon. This is what allows typing the text into the selected field of that tab, without requesting permanent access to any website. |
| scripting | Injects into the active tab the small program that types the pasted text, letter by letter, into the field the user has selected, and lets the user stop typing. |
| storage | Saves the chosen speed and the irregular-pauses option (local storage), and keeps the pasted text only for the browser session so it isn't lost when the panel closes. |
| host_permissions | None. The extension does not request access to any website. |

**Privacy Policy URL (English)**
Pending: publish `docs/privacy-policy.en.md` at a public URL (the Spanish one is `docs/privacy-policy.md`). The dashboard has a single privacy-policy field; use the English one, or a page that links both.


## Graphics & Assets

La tienda permite subir imágenes distintas por idioma. Subir las de `en/` a la ficha en inglés y las de `es/` a la española.

| Asset | Dimensions | Status | Files |
|-------|-----------|--------|-------|
| Store Icon [REQUIRED] | 128×128 PNG | ✅ Ready | `chrome-extension/icons/icon-128.png` |
| Screenshot 1 [REQUIRED] | 1280×800 | ✅ Ready | `store-assets/en/screenshot-1-escribiendo.png`, `store-assets/es/screenshot-1-escribiendo.png` |
| Screenshot 2 [RECOMMENDED] | 1280×800 | ✅ Ready | `store-assets/en/screenshot-2-pasos.png`, `store-assets/es/screenshot-2-pasos.png` |
| Small Promo Tile [RECOMMENDED] | 440×280 | ✅ Ready | `store-assets/en/promo-tile-440x280.png`, `store-assets/es/promo-tile-440x280.png` |
| Marquee Promo Tile | 1400×560 | ⬜ Not created (optional) | |

### Screenshot Notes
Se regeneran con `LANG_UI=en node tools/make_store_assets.js` y `LANG_UI=es node tools/make_store_assets.js`, usando el código y las traducciones reales de la extensión.
1. Un formulario web con el texto escribiéndose y el indicador de progreso con el botón Stop/Detener.
2. El panel de la extensión (texto, velocidad, opciones) con los tres pasos de uso.
Si cambia la interfaz del popup o del indicador, hay que volver a generarlas.

## Permissions Justification

| Permission | Type | Justification |
|------------|------|---------------|
| activeTab | permissions | Da acceso temporal solo a la pestaña actual cuando el usuario pulsa el icono de la extensión. Es lo que permite escribir el texto en el campo seleccionado de esa pestaña, sin pedir acceso permanente a ningún sitio web. |
| scripting | permissions | Inserta en la pestaña activa el pequeño programa que escribe el texto pegado, letra por letra, en el campo que el usuario tiene seleccionado, y que permite detener la escritura. |
| storage | permissions | Guarda la velocidad elegida y la opción de pausas irregulares (almacenamiento local), y el texto pegado solo durante la sesión del navegador para no perderlo al cerrar el panel. |
| (ninguno) | host_permissions | La extensión no solicita permisos de acceso a sitios web. |

## Privacy & Data Use

### Data Collection

**Does the extension collect user data?** No

El código no realiza ninguna petición de red (`fetch`, `XMLHttpRequest`, WebSocket) y no usa `chrome.storage.sync`. El texto del usuario y los ajustes solo se guardan en el navegador del propio usuario (`storage.local` para ajustes, `storage.session` para el texto).

| Data Type | Collected? | Transmitted Off-Device? | Purpose | Shared with Third Parties? |
|-----------|-----------|------------------------|---------|---------------------------|
| Personally identifiable info | No | No | — | No |
| Health info | No | No | — | No |
| Financial info | No | No | — | No |
| Authentication info | No | No | — | No |
| Personal communications | No | No | — | No |
| Location | No | No | — | No |
| Web history | No | No | — | No |
| User activity | No | No | — | No |
| Website content | No | No | — | No |

### Data Use Certification
- [x] Data is NOT sold to third parties
- [x] Data is NOT used for purposes unrelated to the extension's core functionality
- [x] Data is NOT used for creditworthiness or lending purposes

### Remote code
No usa código remoto: todo el JavaScript va dentro del paquete. Sin ofuscación.

## Privacy Policy

**Privacy Policy URL** [REQUIRED]
Pendiente de publicar `docs/privacy-policy.md` (español) y `docs/privacy-policy.en.md` (inglés) en una URL pública (ver README, sección «Publicar en la Chrome Web Store») y rellenar el correo de contacto antes.

## Distribution

**Visibility**: Public (o Unlisted si solo quieres compartir el enlace)
**Regions**: All regions

## Developer Info

**Publisher Name** [REQUIRED]
Pendiente (nombre que verá el público)

**Contact Email** [REQUIRED]
Pendiente. Se muestra públicamente y Google envía aquí los avisos de la revisión.

**Support URL / Email** [RECOMMENDED]
Pendiente (puede ser la página de Issues del repositorio si es público)

## Version History

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| 1.3.0 | 2026-11-08 | Inglés por defecto con selector EN/ES en el panel; README en inglés. | Draft |
| 1.2.0 | 2026-11-08 | Interfaz en inglés y español (según el idioma del navegador); ficha bilingüe. | No enviada |
| 1.1.0 | 2026-11-08 | Pausa mínima por letra (Esc siempre funciona); indicador de progreso; versión mostrada. | No enviada |
| 1.0.0 | 2026-11-08 | Primera versión (no se llegó a publicar). | Draft |

## Review Notes

### Known Issues / Limitations
- **Riesgo de revisión:** una extensión que escribe texto "como si lo tecleara una persona" puede examinarse con más atención, porque podría usarse para saltarse bloqueos de pegado o detección de bots. Las descripciones (ES y EN) deben ser honestas sobre su función (arriba lo es) y no sugerir esos usos. La opción de pausas irregulares se describe tal cual («variación aleatoria»).
- Interfaz en inglés (por defecto) y español. La interfaz sale en inglés por defecto (cualquier idioma del navegador) y se cambia con el selector del panel. Para añadir un idioma: carpeta nueva en `chrome-extension/_locales/<código>/messages.json`, una opción en el selector de `popup.html` y su ficha en el panel.
- No funciona en iframes de otro origen ni en editores que dibujan su propio texto.

### Rejection History
Ninguno todavía.
