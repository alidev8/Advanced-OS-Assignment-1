#!/bin/bash
# quick workaround for logging file path
sysLog="system_monitor_log.txt"

writeLog() {
    currDate=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$currDate - $1" >> "$sysLog"
}

checkMem() {
    echo "--- Current CPU and Memory Usage ---"
    free -m
    top -bn1 | head -n 5
    echo "--- Top 10 Memory Consuming Processes ---"
    ps aux --sort=-%mem | head -n 11 | awk '{print "PID:", $2, "USER:", $1, "CPU%:", $3, "MEM%:", $4}'
}

killProc() {
    read -p "Enter PID to terminate: " tempVal
    
    # basic check for now
    if [ -z "$tempVal" ]; then
        echo "No PID entered."
        return
    fi

    if [ "$tempVal" = "1" ] || [ "$tempVal" = "0" ]; then
        echo "Error. Cannot kill critical system process."
        return
    fi

    procCheck=$(ps -p "$tempVal" -o comm=)
    if [ -z "$procCheck" ]; then
        echo "Process not found in the system."
        return
    fi

    if [ "$procCheck" = "systemd" ] || [ "$procCheck" = "bash" ]; then
        echo "Action denied. Cannot kill $procCheck because it is critical."
        return
    fi

    read -p "Are you sure you want to terminate PID $tempVal? (Y/N): " conf
    if [ "$conf" = "Y" ]; then
        kill -9 "$tempVal"
        echo "Process terminated successfully."
        writeLog "Terminated process PID $tempVal"
    else
        echo "Termination cancelled."
    fi
}

diskCheck() {
    read -p "Enter directory path to inspect: " dirInp
    if [ ! -d "$dirInp" ]; then
        echo "Directory not found on disk."
        return
    fi

    echo "Disk usage for directory $dirInp:"
    du -sh "$dirInp"

    # might improve this later
    echo "Searching for log files larger than 50MB."
    if [ ! -d "ArchiveLogs" ]; then
        mkdir "ArchiveLogs"
        writeLog "Created ArchiveLogs directory"
    fi

    for fileChk in $(find "$dirInp" -type f -size +50M | grep '\.log$'); do
        echo "Found massive log file: $fileChk"
        baseName=$(basename "$fileChk")
        timeStamp=$(date +%s)
        gzip -c "$fileChk" > "ArchiveLogs/${baseName}_${timeStamp}.gz"
        rm "$fileChk"
        writeLog "Archived and removed $fileChk"
    done

    archSize=$(du -sm ArchiveLogs 2>/dev/null | awk '{print $1}')
    if [ -n "$archSize" ] && [ "$archSize" -gt 1024 ]; then
        echo "WARNING: ArchiveLogs directory exceeds 1GB limit."
        writeLog "Warning triggered. ArchiveLogs over 1GB limit"
    fi
}

while true; do
    echo "--- University Data Centre Menu ---"
    echo "1. Process Monitoring and Management"
    echo "2. Disk Inspection and Log Archiving"
    echo "Bye. Exit System"
    read -p "Select an option: " userInp

    if [ "$userInp" = "1" ]; then
        checkMem
        killProc
    elif [ "$userInp" = "2" ]; then
        diskCheck
    elif [ "$userInp" = "Bye" ]; then
        read -p "Do you want to exit? (Y/N): " exitConf
        if [ "$exitConf" = "Y" ]; then
            writeLog "System administrator exited system"
            echo "Goodbye."
            break
        fi
    else
        echo "Invalid choice. Try again."
    fi
done
