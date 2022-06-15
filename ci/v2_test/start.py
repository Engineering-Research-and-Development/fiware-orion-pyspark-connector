import connector_lib as connector
import replier_lib as replier
from pyspark import SparkContext, SparkConf, StorageLevel




import os
import psutil
import time


conf = SparkConf().setAppName("FIWARE Orion-PySpark Connector Demo").set("spark.hadoop.yarn.resourcemanager.address", "local[2]")
sc = SparkContext(conf=conf)


event, ssc = connector.Prime(sc, 5 , StorageLevel.MEMORY_AND_DISK_2)

event = event.flatMap(lambda x: x.entities).map(lambda x: int(x.attrs['price'].value) +10)
response = event.map(lambda x : replier.UnstructuredReplyToBroker('{ "value" :' + str(x) +' }'))
response2 = event.map(lambda x: replier.SemistructuredReplyToBroker(x, '{"value" : %%TOREPLACE%% }'))
response3 = event.map(lambda x : replier.ReplyToBroker(x))
event.saveAsTextFiles("./print/")
response.saveAsTextFiles("./response1/")
response2.saveAsTextFiles("./response2/")
response3.saveAsTextFiles("./response3/")


ssc.start()


try:
	time.sleep(300)
except Exception as e:
	sys.exit(0)
