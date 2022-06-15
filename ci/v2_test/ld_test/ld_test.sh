
hostname=$(hostname -I | tr ' ' '\n' | grep 10)
sed -i "s/0.0.0.0/$hostname/g" ./ci/ld_test/connectorconf.py
mv ./ci/ld_test/connectorconf.py ./ci/PySpark/connectorconf.py
mv ./ci/ld_test/start.py ./ci/PySpark/
cd ./ci/PySpark/

python3 start.py 1> out.txt  2> err.txt &
variable=$!

cd /home/runner/work/fiware-orion-pyspark-connector/fiware-orion-pyspark-connector
sleep 30
echo "exit sleeping"
curl -vX PATCH http://localhost:1026/ngsi-ld/v1/entities/urn:ngsi-ld:Building:store001/attrs/ -d @./ci/ld_test/payload.json -H "Content-Type: application/ld+json" -H "NGSILD-Tenant: orion"
sleep 20


echo "reading output file"
cat ./ci/PySpark/out.txt
rm ./ci/PySpark/out.txt
echo "reading error file"
cat ./ci/PySpark/err.txt
rm ./ci/PySpark/err.txt
ps -e | grep $variable
kill $variable
