hostname=$(hostname -I | tr ' ' '\n' | grep 10)
sed -i "s/0.0.0.0/$hostname/g" ./ci/raw_test/connectorconf.py
mv ./ci/raw_test/connectorconf.py ./ci/PySpark/connectorconf.py
mv ./ci/raw_test/start.py ./ci/PySpark/
python3 ./ci/PySpark/start.py &
variable=$!
sleep 60
chmod 700 ./ci/raw_test/RapidPUT.sh
./ci/raw_test/RapidPUT.sh
sleep 10
kill $variable