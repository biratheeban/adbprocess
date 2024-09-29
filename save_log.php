<?php
// save_log.php

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
        // Initialize a new array for the first log entry
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
?>
