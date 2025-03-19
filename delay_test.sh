DELAY=$1
REPEAT="100"

docker compose exec -T python-processor sh -c "python3 /code/python-processor/main.py $DELAY &"
sleep 1

docker compose exec sec sh -c "ping insec -c $REPEAT" > rtt_$DELAY.txt

docker compose exec python-processor sh -c "pkill -9 python3"