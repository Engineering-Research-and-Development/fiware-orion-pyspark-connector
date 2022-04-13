from connector_lib import *
import conf as connectorconf


def Prime():

	conf = SparkConf().setAppName("TextPicker").set("spark.hadoop.yarn.resourcemanager.address", "local[2]")
	sc = SparkContext(conf=conf)
	ssc = StreamingContext(sc, 10)


	record = ssc.socketTextStream(connectorconf.SOCKETADDRESS, connectorconf.SOCKETPORT, storageLevel=StorageLevel.MEMORY_AND_DISK_2)


	NGSI_event = record.map(lambda x: ParseToNGSILD(x))
	return record, ssc
