# Cómo funciona XML, DTD y las entidades

> Base **conceptual**: qué es XML, qué es un DTD y qué son las entidades.
> **Cómo se explota** (XXE: detección, exfil, error, DTD externa/local, diagramas) → [[vulnerabilities/006-xxe/xxe|entry point de XXE]].

## 1. Qué es XML y qué son las *entities*

**XML** representa **datos** con etiquetas anidadas (`<tag>valor</tag>`). Un parser lo lee y reconstruye la estructura.

Una **XML entity** es una **variable** dentro del documento: definís un nombre y el parser lo **reemplaza por su valor** cada vez que aparece `&nombre;`. Sirve para reutilizar un valor.

Ejemplo típico — una agenda de contactos. Los `<!ELEMENT>` definen la **estructura** (qué etiquetas existen) y el `<!ENTITY>` define una **variable reutilizable**:

```xml
<?xml version="1.0"?>
<!DOCTYPE agenda [
  <!ELEMENT agenda (contacto)>
  <!ELEMENT contacto (nombre, telefono)>
  <!ELEMENT nombre (#PCDATA)>
  <!ELEMENT telefono (#PCDATA)>
  <!ENTITY tel "+54 11 5555-5555">      <!-- ← la entidad -->
]>
<agenda>
  <contacto>
    <nombre>Octavio</nombre>
    <telefono>&tel;</telefono>          <!-- ← se reemplaza por el valor -->
  </contacto>
</agenda>
```

El parser resuelve `&tel;` → `+54 11 5555-5555`. Ese mecanismo de reemplazo es el que, mal configurado, habilita XXE.

## 2. Qué es un DTD (Document Type Definition)

El **DTD** es lo que va dentro del **`<!DOCTYPE …>`**: declara la estructura (elementos) y las **entidades** del documento. Dos formas de incluirlo:

- **DTD interna** — declarada **dentro** del propio documento, entre corchetes:
  ```xml
  <!DOCTYPE foo [ <!ENTITY x "valor"> ]>
  ```
- **DTD externa** — el documento **carga** un DTD que vive en otra URL/archivo:
  ```xml
  <!DOCTYPE foo SYSTEM "http://ejemplo.com/schema.dtd">
  ```

La palabra clave **`SYSTEM`** le dice al parser que el valor es una **URI externa** (`file://`, `http://`, `ftp://`…). Es la base de las *entidades externas*.

## 3. Tipos de entidad

### Entidad general (`&`)
La normal: se define en el DTD y se referencia con **`&nombre;`** en el **cuerpo** del XML.
```xml
<!DOCTYPE foo [ <!ENTITY saludo "hola"> ]>
<msg>&saludo;</msg>          <!-- → <msg>hola</msg> -->
```

### Entidad de parámetro (`%`)
Una variante que **solo vive dentro del DTD** y se referencia con **`%nombre;`**. Se declara con `%` entre `ENTITY` y el nombre:
```xml
<!ENTITY % miparam "valor">
%miparam;
```
Su particularidad: como solo se puede usar **dentro del DTD**, sirve para construir/encadenar otras declaraciones. (Ese detalle es justo lo que se aprovecha en el XXE ciego → ver entry point.)

> Regla mental: **`&x;` = cuerpo del XML** · **`%x;` = dentro del DTD**.

---

> [!note] Seguir
> - Explotarlo (detección, in-band vs blind, exfil/error/DTD externa/local, diagramas) → [[vulnerabilities/006-xxe/xxe|entry point de XXE]].
> - Los 9 labs con payload por lab → [[vulnerabilities/006-xxe/labs/README|labs de XXE]].
