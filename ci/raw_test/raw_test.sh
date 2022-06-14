hostname=$(hostname -I | tr ' ' '\n' | grep 10)


sed -i "s/0.0.0.0/$hostname/g" ./ci/raw_test/subscription.json
cat ./ci/raw_test/subscription.json
curl -X POST http://localhost:1026/v2/entities/ -d @./ci/raw_test/new_entity.json --header "Content-Type: application/json"
curl -X POST http://localhost:1026/v2/subscriptions/ -d @./ci/raw_test/subscription.json --header "Content-Type: application/json"
sleep 10
sed -i "s/0.0.0.0/$hostname/g" ./ci/raw_test/connectorconf.py
cat ./ci/raw_test/connectorconf.py
mv ./ci/raw_test/connectorconf.py ./ci/PySpark/connectorconf.py
mv ./ci/raw_test/start.py ./ci/PySpark/
python3 ./ci/PySpark/start.py &
variable=$!
sleep 60
chmod 700 ./ci/raw_test/RapidPUT.sh
./ci/raw_test/RapidPUT.sh > /dev/null
sleep 10
kill $variable
