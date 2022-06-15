hostname=$(hostname -I | tr ' ' '\n' | grep 10)
sed -i "s/0.0.0.0/$hostname/g" ./ci/raw_test/connectorconf.py
mv ./ci/raw_test/connectorconf.py ./ci/PySpark/connectorconf.py
mv ./ci/raw_test/start.py ./ci/PySpark/
cd ./ci/PySpark/
python3 start.py 1> out.txt  2> err.txt &
#spark-submit --py-files ./ci/PySpark/start.py ./ci/PySpark/connectorconf.py ./ci/PySpark/connector_lib.py ./ci/PySpark/replier_lib.py ./ci/PySpark/replyconf.py 
variable=$!

cd /home/runner/work/fiware-orion-pyspark-connector/fiware-orion-pyspark-connector
sleep 30
echo "exit sleeping"
chmod 700 ./ci/v2_test/RapidPUT.sh
./ci/v2_test/RapidPUT.sh
sleep 20

echo "reading output file"
cat ./ci/PySpark/out.txt
rm ./ci/PySpark/out.txt
echo "reading error file"
cat ./ci/PySpark/err.txt
rm ./ci/PySpark/err.txt
ps -e | grep $variable
kill $variable
