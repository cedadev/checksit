#!/bin/bash

prompt=false
[ "$1" == "--prompt" ] || [ "$1" == "-p" ] && prompt=true

mapfile -t lines < cli_tests.txt

for i in $(seq ${#lines[@]}) ; do 
    CMD=${lines[$i]} 

    echo
    [ ! "$CMD" ] || [[ "$CMD" =~ \# ]] && continue
    echo "[INFO] Running: "
    
    count=0
    for i in $(echo $CMD); do 
        [ $count -eq 0 ] && echo "$ checksit check"
        [ $count -ge 2 ] && echo "     $i"
        let count+=1
    done

    if [ $prompt == "true" ]; then
        echo
        echo "Press ENTER to continue..."
        read waiter
        if [ "$waiter" == "q" ]; then
            echo "[INFO] Exiting!"
            exit
        fi
    fi
 
    $CMD

    if [ $? -ne 0 ]; then
        echo
        echo "[ERROR] The following command failed...so aborting: $CMD"
        break
    fi

    echo
    echo "=========================================================================="
done 
       
