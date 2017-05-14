#!/bin/bash

logDir="$1"
if [ ! -d "$logDir" ]; then
    echo "$logDir is not a directory"
    exit 1
fi
file_name=$(date +'%Y%m')
logFile="$logDir/$file_name"

if [ ! -f $logFile ]; then
    echo -e "date core1 core2" > "$logFile"
fi

now=$(date +'%d%H%M%S')

result=$(sensors | grep -o Core.*\( | grep -o +.*C)
echo $now $result >> "$logFile"