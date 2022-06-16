import connector_lib as connector
import replier_lib as replier
from pyspark import SparkContext, SparkConf, StorageLevel




import os
import psutil
import time


conf = SparkConf().setAppName("FIWARE Orion-PySpark Connector Demo").set("spark.hadoop.yarn.resourcemanager.address", "local[2]")
sc = SparkContext(conf=conf)


event, ssc = connector.Prime(sc, 5 , StorageLevel.MEMORY_AND_DISK_2)
event = event.flatMap(lambda x: x.entities).map(lambda x: x.attrs['category'].type)

event.pprint()


ssc.start()
ssc.awaitTerminationOrTimeout(90)
