
hostname=$(hostname -I | tr ' ' '\n' | grep 10)
sed -i "s/0.0.0.0/$hostname/g" ./ci/v2_test/connectorconf.py
mv ./ci/v2_test/connectorconf.py ./ci/PySpark/connectorconf.py
mv ./ci/v2_test/start.py ./ci/PySpark/
mv ./ci/v2_test/Test.txt ./ci/PySpark/
cd ./ci/PySpark/

python3 start.py 1> out.txt 2> err.txt &
variable=$!

cd /home/runner/work/fiware-orion-pyspark-connector/fiware-orion-pyspark-connector
sleep 10
echo "exit sleeping"
chmod 700 ./ci/v2_test/RapidPUT.sh
./ci/v2_test/RapidPUT.sh
fg 1
sleep 20

ps -e | grep $variable
kill -SIGINT $variable


echo "reading output file"
cat ./ci/PySpark/out.txt
rm ./ci/PySpark/out.txt
echo "reading error file"
cat ./ci/PySpark/err.txt
rm ./ci/PySpark/err.txt


