<?php

$memory_kb = array_sum($memory_data);

$stmt = $conn->prepare ("INSERT INTO processlog(process_name, process_id,memory_kb, timestamp)
VALUES (:process_name,process_id,memory_kb,timestamp) ") ;
$stmt->bindParam(":process_name",$name,PDO::PARAM_STR);
$stmt->bindParam(":process_id",$pid,PDO::PARAM_INT);
$stmt->bindParam(":memory_kb",$memory_kb,PDO::PARAM_STR);
$stmt->bindParam(":memory_data",$memory_data,PDO::PARAM_STR);
$stmt->bindParam(":timestamp",$name,PDO::PARAM_STR);

?>