#!/bin/bash

while read CMD ; do
    echo
    [ ! "$CMD" ] || [[ "$CMD" =~ \# ]] && continue
    echo "[INFO] Running: $CMD"
    $CMD

    if [ $? -ne 0 ]; then
        echo
        echo "[ERROR] The following command failed...so aborting: $CMD"
        break
    fi
done < cli_tests.txt
       
