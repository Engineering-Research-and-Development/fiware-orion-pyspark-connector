
hostname=$(hostname -I | tr ' ' '\n' | grep 10)
sed -i "s/0.0.0.0/$hostname/g" ./ci/v2_test/connectorconf.py
mv ./ci/v2_test/connectorconf.py ./ci/PySpark/connectorconf.py
mv ./ci/v2_test/start.py ./ci/PySpark/
mv ./ci/v2_test/Test.txt ./ci/PySpark/
cd ./ci/PySpark/

python3 start.py 1> out.txt  2> err.txt &
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

find ./ci/PySpark/print/ -type f | grep part 
find ./ci/PySpark/print/ -type f | grep part | xargs cat 
