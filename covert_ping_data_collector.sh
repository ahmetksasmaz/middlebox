EXPERIMENT_FILE=$1
REPEAT=$2

rm -rf $EXPERIMENT_FILE

# Restart mitm
docker compose exec python-processor sh -c "pkill -15 python3"
docker compose exec -T python-processor sh -c "python3 /code/python-processor/dropper_w_log.py 0.05 1 &"
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
    docker compose exec insec sh -c "pkill -15 tcpdump"
}

send_random_k_n_times() {
    for i in $(seq 1 $REPEAT); do
        K_BITS=$((RANDOM % 100 + 1))
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
    done
}

send_random_k_n_times

docker compose exec python-processor sh -c "pkill -15 python3"