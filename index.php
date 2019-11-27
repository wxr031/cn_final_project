<!DOCTYPE html>
<html>
	<head>
		<title>CNMessage</title>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
		<link rel="stylesheet" href="./css/bootstrap.min.css" >
		<link rel="stylesheet" href="./css/main.css" >
	</head>
	<body>
		<?php
			$page = "main";
			if (isset($_GET["page"])) {
				if (in_array($_GET["page"], array("main", "registration", "messaging", "file_transfer"))) {
					$page = $_GET["page"];
				}
				else {
					$page = "error";
				}
			}
			require "template/nav.php";
			require "template/" . $page . ".php";
		?>
		<script defer src="https://use.fontawesome.com/releases/v5.0.0/js/all.js"></script>
		<script defer src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
		<script src="./js/main.js"></script>
		<script src="./js/bootstrap.min.js"></script>
		
	</body>
</html>

