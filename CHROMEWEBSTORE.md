# Chrome Web Store Listing — PasteScribe

> Last Updated: 2026-11-08

## Store Listing

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

Versión 1.1.0: la velocidad mínima evita que el texto aparezca de golpe y permite detenerlo siempre con Esc.
```

**Category** [REQUIRED]
Productivity (Productividad)

**Single Purpose** [REQUIRED]
Escribe, letra por letra, un texto pegado por el usuario en el campo de texto enfocado de la pestaña activa.

**Primary Language** [REQUIRED]
Spanish (español)

## Graphics & Assets

| Asset | Dimensions | Status | Filename |
|-------|-----------|--------|----------|
| Store Icon [REQUIRED] | 128×128 PNG | ✅ Ready | `chrome-extension/icons/icon-128.png` |
| Screenshot 1 [REQUIRED] | 1280×800 | ✅ Ready | `store-assets/screenshot-1-escribiendo.png` |
| Screenshot 2 [RECOMMENDED] | 1280×800 | ✅ Ready | `store-assets/screenshot-2-pasos.png` |
| Small Promo Tile [RECOMMENDED] | 440×280 | ✅ Ready | `store-assets/promo-tile-440x280.png` |
| Marquee Promo Tile | 1400×560 | ⬜ Not created (opcional) | |

### Screenshot Notes
Se regeneran con `node tools/make_store_assets.js`, usando el código real de la extensión.
1. Un formulario web con el texto escribiéndose y el indicador de progreso con el botón Detener.
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
Pendiente de publicar `docs/privacy-policy.md` en una URL pública (ver README, sección «Publicar en la Chrome Web Store») y rellenar el correo de contacto antes.

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
| 1.1.0 | 2026-11-08 | Pausa mínima por letra (Esc siempre funciona); indicador de progreso; versión mostrada. | Draft |
| 1.0.0 | 2026-11-08 | Primera versión (no se llegó a publicar). | Draft |

## Review Notes

### Known Issues / Limitations
- **Riesgo de revisión:** una extensión que escribe texto "como si lo tecleara una persona" puede examinarse con más atención, porque podría usarse para saltarse bloqueos de pegado o detección de bots. La descripción debe ser honesta sobre su función (arriba lo es) y no sugerir esos usos. La opción de pausas irregulares se describe tal cual («variación aleatoria»).
- Solo interfaz en español. Si se quiere ampliar a otros idiomas, habría que añadir traducciones de la interfaz y de la ficha.
- No funciona en iframes de otro origen ni en editores que dibujan su propio texto.

### Rejection History
Ninguno todavía.
