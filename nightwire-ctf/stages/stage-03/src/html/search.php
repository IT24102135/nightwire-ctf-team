<?php
// Disable fatal exceptions so players can see the raw SQL errors
mysqli_report(MYSQLI_REPORT_OFF);

$conn = new mysqli("127.0.0.1", "root", "root", "solace");

if ($conn->connect_error) {
    die("DB Connection Error: " . $conn->connect_error);
}

$q = $_GET['q'];

// VULNERABLE: Direct concatenation of the $q parameter
$sql = "SELECT ticket_id, notes FROM tickets WHERE ticket_id = '$q'";
$result = $conn->query($sql);

if ($result) {
    while($row = $result->fetch_assoc()) {
        echo "ID: " . $row["ticket_id"] . " | " . $row["notes"] . "<br>";
    }
} else {
    // Deliberately verbose error to aid SQLi discovery
    echo "SQL Error: " . $conn->error;
}
?>
