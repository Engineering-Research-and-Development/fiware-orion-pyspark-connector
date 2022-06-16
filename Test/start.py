import connector_lib as connector
import replier_lib as replier
from pyspark import SparkContext, SparkConf, StorageLevel

import os
import psutil
import time


conf = SparkConf().setAppName("FIWARE Orion-PySpark Connector Demo").set("spark.hadoop.yarn.resourcemanager.address", "local[2]")
sc = SparkContext(conf=conf)


event, ssc = connector.Prime(sc, 5 , StorageLevel.MEMORY_AND_DISK_2)

event = event.flatMap(lambda x: x.entities).map(lambda x: x.attrs['price'].value)
response = event.map(lambda x : replier.UnstructuredReplyToBroker('{ "value" :' + str(20) +' }'))
response2 = event.map(lambda x: replier.SemistructuredReplyToBroker("20", '{"value" : %%TOREPLACE%% }'))
response3 = event.map(lambda x : replier.ReplyToBroker("20"))
event.pprint()
response.pprint()
response2.pprint()
response3.pprint()


ssc.start()
ssc.awaitTerminationOrTimeout(90)
