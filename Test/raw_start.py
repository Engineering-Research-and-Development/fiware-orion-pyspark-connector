import as connector
from pyspark import SparkContext, SparkConf, StorageLevel

import os
import psutil
import time


conf = SparkConf().setAppName("FIWARE Orion-PySpark Connector Demo").set("spark.hadoop.yarn.resourcemanager.address", "local[2]")
sc = SparkContext(conf=conf)



event, ssc = connector.Prime(sc, 10 , StorageLevel.MEMORY_AND_DISK_2)
event.pprint()


ssc.start()
ssc.awaitTerminationOrTimeout(90)
