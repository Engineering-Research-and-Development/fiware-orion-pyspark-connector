
hostname=$(hostname -I | tr ' ' '\n' | grep 10)
sed -i "s/0.0.0.0/$hostname/g" ./ci/v2_test/connectorconf.py
mv ./ci/v2_test/connectorconf.py ./ci/PySpark/connectorconf.py
mv ./ci/v2_test/start.py ./ci/PySpark/
mv ./ci/v2_test/Test.txt ./ci/PySpark/
cd ./ci/PySpark/
python3 start.py &
variable=$!
cd /home/runner/work/fiware-orion-pyspark-connector/fiware-orion-pyspark-connector
sleep 30
echo "exit sleeping"
chmod 700 ./ci/v2_test/RapidPUT.sh
./ci/v2_test/RapidPUT.sh 1> /dev/null 2> /dev/null
sleep 50
echo "reading output file"
cat ./ci/PySpark/out.txt
echo "reading error file"
cat ./ci/PySpark/err.txt
ps -e | grep $variable
kill $variable
