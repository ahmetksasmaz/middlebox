#!/bin/bash

# Infinite loop script
# Press Ctrl+C to exit

COUNTER=(RANDOM % 10 + 1)

while true; do

    echo $(wc -l < code/python-processor/covert_ping_dataset.txt) 

    if [ -f "code/python-processor/covert_ping_dataset.txt" ] && [ $(wc -l < code/python-processor/covert_ping_dataset.txt) -gt 100000 ]; then
        echo "Reached 100.000 lines limit. Exiting..."
        break
    fi

    N_TIMES=$((RANDOM % 10 + 1))
    bash covert_ping_data_collector.sh temp.out $N_TIMES

    COUNTER=$((COUNTER - 1))
    if [ $COUNTER -le 0 ]; then
        docker compose restart
        COUNTER=$((RANDOM % 10 + 1))
    fi

done