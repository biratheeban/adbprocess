<?php
// save_log.php

$log_directory = "logs/";
if (!file_exists($log_directory)) {
    mkdir($log_directory, 0777, true);
}
// Get JSON data from POST request
$log_data = file_get_contents('php://input');

$date = date('Y-m-d');
$log_file_name = $log_directory . "android_profiling_log_" . $date . ".json";

if ($log_data) {

    $decoded_data = json_decode($log_data, true);

    if (json_last_error() !== JSON_ERROR_NONE) {
        echo "Invalid JSON data.";
        exit;
    }

    if (file_exists($log_file_name)) {
        $existing_data = file_get_contents($log_file_name);
        $data_array = json_decode($existing_data, true);
        
        if (!is_array($data_array)) {
            $data_array = [];
        }
    } else {
        $data_array = [];
    }

    $data_array[] = $decoded_data;
    $json_data = json_encode($data_array, JSON_PRETTY_PRINT);
    file_put_contents($log_file_name, $json_data);

    echo "Log saved successfully.";
} else {
    echo "No log data received.";
}
?>
