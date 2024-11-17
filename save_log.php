<?php
// save_log.php;
//CONFIG
define('DB_SERVER', 'localhost');
define('DB_USERNAME', 'root');
define('DB_PASSWORD', 'apppass');
define('DB_NAME', 'processlog_db');


// Directory to save log files
$log_directory = "logs/";
if (!file_exists($log_directory)) {
    mkdir($log_directory, 0777, true);
}

// Get JSON data from POST request
$log_data = file_get_contents('php://input');

// Get the current date to create a daily log file
$date = date('Y-m-d');
$log_file_name = $log_directory . "android_profiling_log_" . $date . ".json";

if ($log_data) {
    // Decode the incoming JSON data
    $decoded_data = json_decode($log_data, true);
    $memory_data=$decoded_data['memory_data'];
    $timestamp=$decoded_data['timestamp'];
    saveLogDataToDb($timestamp,$memory_data);

    // Check if decoding was successful
    if (json_last_error() !== JSON_ERROR_NONE) {
        echo "Invalid JSON data.";
        exit;
    }

    // Check if the log file exists
    if (file_exists($log_file_name)) {
        // Read existing data
        $existing_data = file_get_contents($log_file_name);
        $data_array = json_decode($existing_data, true);
        
        // Initialize as an empty array if file is empty or not a valid JSON
        if (!is_array($data_array)) {
            $data_array = [];
        }
    } else {
        $data_array = [];
    }

    // Append the new log data
    $data_array[] = $decoded_data;

    // Encode the updated array back to JSON
    $json_data = json_encode($data_array, JSON_PRETTY_PRINT);

    // Write the JSON data back to the file
    file_put_contents($log_file_name, $json_data);
    

    echo "Log saved successfully.";
} else {
    echo "No log data received.";
}
//CONNECT
function connect(){
    $pdo;
try {
    $pdo = new PDO(
        "mysql:host=" . DB_SERVER . ";dbname=" . DB_NAME . ";charset=utf8",
        DB_USERNAME,
        DB_PASSWORD,
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_PERSISTENT => true, 
        ]
    );
} catch (PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
}
    return $pdo;
}

function saveLogDataToDb($timestamp,$memory_data){
        $conn=connect();
        $stmt = $conn->prepare("INSERT INTO processlog (process_name, process_id, memory_kb, timestamp) 
                                VALUES (:process_name, :process_id, :memory_kb, :timestamp)");

        foreach ($memory_data as $process) {
            $stmt->execute([
                ':process_name' => $process['process_name'],
                ':process_id' => (int)$process['process_id'],
                ':memory_kb' => (double)$process['memory_kb'],
                ':timestamp' => $timestamp,
            ]);
        }
}
?>
