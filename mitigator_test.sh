EXPERIMENT_FILE=$1
SCENARIO_NUMBER=$2
REPEAT=$3
DROP_RATE=$4
MITIGATION_RATE=$5
K_BITS=$6
CONSISTENT_COUNT=0

rm -rf $EXPERIMENT_FILE

# Restart mitm
docker compose exec python-processor sh -c "pkill -9 python3"
docker compose exec -T python-processor sh -c "python3 /code/python-processor/mitigator.py $DROP_RATE $MITIGATION_RATE &"
sleep 0.5

send_0_bit() {
    docker compose exec sec sh -c "ping insec -0 -i 0.2" | tail -n 3 >> $EXPERIMENT_FILE
}

send_1_bit() {
    docker compose exec sec sh -c "ping insec -1 -i 0.2" | tail -n 3 >> $EXPERIMENT_FILE
}

send_eof(){
    docker compose exec sec sh -c "ping insec -2 -i 0.2" | tail -n 3 >> $EXPERIMENT_FILE

    while [ -z "$(tail -n 1 $EXPERIMENT_FILE)" ]; do
        docker compose exec sec sh -c "ping insec -2 -i 0.2" | tail -n 3 >> $EXPERIMENT_FILE
    done
}

start_insec(){
    docker compose exec insec sh -c "rm -rf /code/insec/10.1.0.21.txt"
    docker compose exec -T insec sh -c "tcpdump -i eth0 icmp and icmp[icmptype]=icmp-echo -n -l | python3 /code/insec/dump_parser.py -f &"
    sleep 0.5
}

stop_insec(){
    docker compose exec insec sh -c "pkill -9 tcpdump"
}

cmp_insec_result(){
    if [ "$1" == "$(docker compose exec insec sh -c "cat /code/insec/10.1.0.21.txt")" ]; then
        CONSISTENT_COUNT=$((CONSISTENT_COUNT + 1))
    fi
}

# Scenario Number 1 : Sending bit-0 N times

send_0_n_times() {
    for i in $(seq 1 $REPEAT); do

        echo "Iteration $i of $REPEAT"

        start_insec
        send_0_bit
        send_eof
        stop_insec
        cmp_insec_result "0"

        echo "Consistent Rate : [$CONSISTENT_COUNT / $REPEAT]"
    done

    echo "Consistent Rate : [$CONSISTENT_COUNT / $REPEAT]" >> $EXPERIMENT_FILE
}

# Scenario Number 2 : Sending bit-1 N times
send_1_n_times() {
    for i in $(seq 1 $REPEAT); do

        echo "Iteration $i of $REPEAT"

        start_insec
        send_1_bit
        send_eof
        stop_insec
        cmp_insec_result "1"

        echo "Consistent Rate : [$CONSISTENT_COUNT / $REPEAT]"
    done

    echo "Consistent Rate : [$CONSISTENT_COUNT / $REPEAT]" >> $EXPERIMENT_FILE
}

# Scenario Number 3 : Sending k bits N times
send_k_n_times() {
    for i in $(seq 1 $REPEAT); do

        echo "Iteration $i of $REPEAT"

        RANDOM_BINARY_STRING=$(head /dev/urandom | LC_ALL=C tr -dc '01' | head -c $K_BITS)

        start_insec
        
        for (( j=0; j<$K_BITS; j++ )); do
            if [ "${RANDOM_BINARY_STRING:$j:1}" == "0" ]; then
                send_0_bit
            else
                send_1_bit
            fi
        done

        send_eof
        stop_insec
        cmp_insec_result $RANDOM_BINARY_STRING
        
        echo "Consistent Rate : [$CONSISTENT_COUNT / $REPEAT]"
    done

    echo "Consistent Rate : [$CONSISTENT_COUNT / $REPEAT]" >> $EXPERIMENT_FILE
}

if [ "$SCENARIO_NUMBER" == "1" ]; then
    send_0_n_times
elif [ "$SCENARIO_NUMBER" == "2" ]; then
    send_1_n_times
elif [ "$SCENARIO_NUMBER" == "3" ]; then
    send_k_n_times
fi