<?php

// Receive data from a POST request or any other source
$audio = $_POST['audio'] ?? '';
$text = $_POST['text'] ?? '';
$fresh = isset($_POST['fresh']) ? '--fresh' : '';  // assuming fresh is a checkbox or boolean value
$low_bandwidth = isset($_POST['low_bandwidth']) ? '--low_bandwidth' : ''; // similar to fresh
$costs = isset($_POST['costs']) ? '--costs' : ''; // similar to fresh
$model = $_POST['model'] ?? 'gpt-4'; // use default if not provided
$output = $_POST['output'] ?? 'text'; // use default if not provided

// Construct the command
$command = "/usr/local/antheia/venv/bin/python3 /usr/local/antheia/antheia.py";
$command .= "--audio " . escapeshellarg($audio) . " ";
$command .= "--text " . escapeshellarg($text) . " ";
$command .= "$fresh ";
$command .= "$low_bandwidth ";
$command .= "$costs ";
$command .= "--model " . escapeshellarg($model) . " ";
$command .= "--output " . escapeshellarg($output);

// Execute the command
$output = shell_exec($command);

echo $output;
