<main role="main" class="container text-center">
	<form class="form-signin" method="post" action="registration.php">
		<div class="h1 mb-5 mt-3">Registration</div>
		<div class="d-flex justify-content-center mt-2 mb-2">
			<i class="fas fa-user h3 mr-3 mt-1"></i>
			<input type="text" id="username_input" class="form-control w-25" placeholder="Username" required autofocus>
		</div>
		<div class="d-flex justify-content-center mt-2 mb-2">
			<i class="fas fa-key h3 mr-3 mt-1"></i>
			<input type="password" id="password_input" class="form-control w-25" placeholder="Password" required>
		</div>
		<input type="submit" id="submit-registration" class="btn btn-lg btn-primary mt-3" value="Register">
	</form>
	<?php
		$reg_status = "";
		if (isset($_POST["username"]) && isset($_POST["password"])) {
			function sanitize_input($input) {
				if (!preg_match("[A-Za-z0-9_]*", $input)) {
					return false;
				}
				return true;
			}

			$host = "localhost";
			$name = "cn_message";
			$pass = "";
			$db = "cn_auth";

			$reg_name = $_POST["username"];
			$reg_pass = $_POST["password"];

			if (sanitize_input($reg_name) === false || sanitize_input($reg_pass) === false) {
				$reg_status = "Invalid username/password: Username/Password must contain only alphanumeric characters.";
			}
			else {
				$conn = new mysqli($host, $name, $pass, $db);
				if ($conn->connect_error) {
					die("Cannot establish connection to the mysql server: " . $conn->connect_error);
				}
				$stmt = $conn->prepare("SELECT * FROM auth WHERE username = ?");
				$stmt->bind_param("s", $reg_name);
				$stmt->execute();
				$result = $stmt->get_result();
				if ($result->num_rows !== 0) {
					$reg_status = "Username already exists";
				}
				else {
					$stmt = $conn->prepare("INSERT INTO auth (username, password) VALUES(?, ?)");
					$stmt->bind_param("ss", $reg_name, $reg_pass);
					$stmt->execute();
					$reg_status = "Registration OK";

				}
			}
		}

	?>
</main>
