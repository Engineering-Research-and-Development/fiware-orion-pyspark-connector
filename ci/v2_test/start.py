import connector
from pyspark import SparkContext, SparkConf, StorageLevel




import os
import psutil
import time


conf = SparkConf().setAppName("FIWARE Orion-PySpark Connector Demo").set("spark.hadoop.yarn.resourcemanager.address", "local[2]")
sc = SparkContext(conf=conf)


event, ssc = connector.Prime(sc, 5 , StorageLevel.MEMORY_AND_DISK_2)

event = event.flatMap(lambda x: x.entities).map(lambda x: x.attrs['price'].value)
response = event.map(lambda x : connector.UnstructuredReplyToBroker('{ "value" :' + str(20) +' }'))
response2 = event.map(lambda x: connector.SemistructuredReplyToBroker(20, '{"value" : %%TOREPLACE%% }'))
response3 = event.map(lambda x : connector.ReplyToBroker(20))
event.pprint()
response.pprint()
response2.pprint()
response3.pprint()


ssc.start()


try:
	time.sleep(300)
except Exception as e:
	sys.exit(0)
