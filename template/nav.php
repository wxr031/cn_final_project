<nav class="navbar navbar-expand-md navbar-dark bg-dark fixed-top">
	<div class="collapse navbar-collapse" id="navbarsExampleDefault">
		<ul class="navbar-nav mr-auto">
			<li class="nav-item <?php if ($page === "main") echo "active"?>">
				<a class="nav-link" href="index.php?">Main Page</a>
			</li>
			<li class="nav-item <?php if ($page === "registration") echo "active"?>">
				<a class="nav-link" href="index.php?page=registration">Registration</a>
			</li>
			<li class="nav-item <?php if ($page === "messaging") echo "active"?>">
				<a class="nav-link" href="index.php?page=messaging">Messaging</a>
			</li>
			<li class="nav-item <?php if ($page === "file_transfer") echo "active"?>">
				<a class="nav-link" href="index.php?page=file_transfer">File Transfer</a>
			</li>
		</ul>
	</div>
</nav>
