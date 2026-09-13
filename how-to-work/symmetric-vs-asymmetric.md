# Cómo funciona el cifrado simétrico vs asimétrico

> Base **conceptual**: la diferencia entre una **clave única compartida** y un **par pública/privada**. Aplica tanto a **cifrar** (confidencialidad) como a **firmar** (integridad/autenticidad).
> Dónde se usa: firmas de **JWT** (`HS256` vs `RS256`) → [[how-to-work/jwt|Cómo funciona un JWT]].

## Simétrico — una sola clave

**La misma clave** hace las dos operaciones (cifrar/descifrar, o firmar/verificar). Quien tiene esa clave puede **hacer todo**.

- **Ventaja:** rápido y simple.
- **Problema:** las dos partes tienen que **compartir el secreto** de antemano, y si se filtra, se acabó.
- **Ejemplos:** **AES** (cifrado), **HMAC** (firma/MAC con secreto).

```
firmar:    firma = HMAC(mensaje, secreto)
verificar: recalcular HMAC(mensaje, secreto) y comparar   ← MISMO secreto
```

## Asimétrico — par pública / privada

Dos claves **matemáticamente relacionadas**: lo que hace una, **solo lo deshace la otra**. La **privada** se guarda en secreto; la **pública** se puede repartir.

- **Ventaja:** no hace falta compartir un secreto; la pública puede ser conocida por todos.
- **Dos usos distintos** (según qué clave se use primero):
  - **Cifrar (confidencialidad):** cifrás con la **pública** → solo la **privada** descifra.
  - **Firmar (integridad/autenticidad):** firmás con la **privada** → cualquiera verifica con la **pública**.
- **Ejemplos:** **RSA**, **ECDSA**.

```
firmar:    firma = sign(mensaje, PRIVADA)
verificar: verify(mensaje, firma, PÚBLICA)                 ← claves DISTINTAS
```

## Comparación

| | **Simétrico** | **Asimétrico** |
| --- | --- | --- |
| Claves | **una** compartida | **par** pública + privada |
| ¿El que verifica puede firmar? | **Sí** (misma clave) | **No** (necesita la privada) |
| Reparto del secreto | hay que compartirlo | la pública se publica |
| Velocidad | rápido | más lento |
| Ejemplos | AES, HMAC | RSA, ECDSA |

> **Regla mental:** simétrico → *firmar = verificar* (misma clave). Asimétrico → *firmar ≠ verificar* (privada firma, pública verifica).

> [!note] Por qué importa en seguridad
> Muchos bugs salen de **confundir los dos modelos**: p. ej. tratar una **clave pública** (que es, del server) como si fuera un **secreto simétrico** y firmar con ella → *algorithm confusion* en JWT (`RS256 → HS256`). → [[vulnerabilities/018-jwt-attacks/jwt-attacks|ataques JWT]].
