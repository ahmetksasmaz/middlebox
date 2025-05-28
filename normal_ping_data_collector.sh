REPEAT=$1

# Restart mitm
docker compose exec python-processor sh -c "pkill -15 python3"
docker compose exec -T python-processor sh -c "python3 /code/python-processor/dropper_w_log.py 0.05 0 &"
sleep 0.5

execute_ping_n_times() {
    for i in $(seq 1 $REPEAT); do
        TIME=$((RANDOM % 10 + 1))

        docker compose exec sec sh -c "/code/sec/ping insec -w $TIME"
    done
}

execute_ping_n_times

docker compose exec python-processor sh -c "pkill -15 python3"