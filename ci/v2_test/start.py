import connector_lib as connector
import replier_lib as replier
from pyspark import SparkContext, SparkConf, StorageLevel




import os
import psutil
import time


conf = SparkConf().setAppName("FIWARE Orion-PySpark Connector Demo").set("spark.hadoop.yarn.resourcemanager.address", "local[2]")
sc = SparkContext(conf=conf)



event, ssc = connector.Prime(sc, 10 , StorageLevel.MEMORY_AND_DISK_2)
event = event.flatMap(lambda x: x.entities).map(lambda x: x.attrs['price'].value)
#response = event.map(lambda x : replier.UnstructuredReplyToBroker('{ "value" :' + str(x) +' }'))
response2 = event.map(lambda x: replier.SemistructuredReplyToBroker(x, '{"value" : %%TOREPLACE%% }'))
#response3 = event.map(lambda x : replier.ReplyToBroker(x))
event.pprint()
#response.pprint()
response2.pprint()
#response3.pprint()


ssc.start()


try:
	time.sleep(300)
except Exception as e:
	sys.exit(0)
