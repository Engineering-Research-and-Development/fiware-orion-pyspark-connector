hostname=$(hostname -I | tr ' ' '\n' | grep 10)

cd ./Test
mkdir package

sed -i "s/0.0.0.0/$hostname/g" ld_connectorconf.py
mv ld_connectorconf.py ./package/connectorconf.py
mv ld_start.py ./package
mv __init__.py ./package


cd /home/runner/work/fiware-orion-pyspark-connector/fiware-orion-pyspark-connector/
mv ./ci/PySpark/connector_lib.py ./Test/package
mv ./ci/PySpark/replier_lib.py ./Test/package
mv ./ci/PySpark/replyconf.py ./Test/package

ls -l ./Test/package/
