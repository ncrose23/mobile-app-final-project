#!/bin/bash

# Define the directory containing your APK files
apk_dir="apps"
output_dir="decoded_apks"

# Loop through each APK file in the directory
for apk_file in "$apk_dir"/*.apk; do
    # Extract the filename without extension
    filename=$(basename "$apk_file" .apk)
    folderpath="$output_dir/$filename"
    
    # # Run apktool to disassemble the APK
    echo | apktool d "$apk_file" -o "$folderpath"
    # # Press Enter to continue
    # echo "" | read -r
done
