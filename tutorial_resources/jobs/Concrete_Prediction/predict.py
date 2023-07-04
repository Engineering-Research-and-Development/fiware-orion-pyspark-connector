# cd /data/Concrete_Prediction
# spark-submit predict.py --py-files model.pickle

from FPC import connector
#import connectorconf

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType
from pyspark import SparkContext, SparkConf, StorageLevel
import time
from datetime import datetime

import sklearn


import os
import psutil
import time
import pickle
import pandas as pd
import numpy as np



spark = SparkSession.builder.appName("FIWARE Orion-PySpark Connector Demo").master("local[5]").config("spark.port.maxRetries", 100).getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
sc = spark.sparkContext


loaded_model = pickle.load(open("./model.pickle", "rb"))


###### CONNECTOR CONFIGURATION #######

connector.RECV_SINGLETON.http_address = "172.28.1.1"
connector.RECV_SINGLETON.http_port = 8061




###########################################

def Predict(iter):

    connector.REPL_SINGLETON.fiware_service = "tutorial"
    connector.REPL_SINGLETON.fiware_servicepath = "/pyspark"
    connector.REPL_SINGLETON.placeholder_string = "%%PLACEHOLDER%%"
    
    for entity in iter:
        values = np.array([val.value for val in entity.attrs.values()]).reshape(1, -1)
        df = pd.DataFrame(values, columns=list(entity.attrs.keys()))
        record = df.drop('strength', axis=1).to_numpy().reshape(1,-1)
        prediction = loaded_model.predict(record)[0]
        MAE = np.abs(df['strength'].to_numpy() - prediction)
        body = '''{"predicted_strength": {"value": %%PLACEHOLDER%% }, "prediction_error" : {"value": %%PLACEHOLDER%% }}'''
        response = connector.SemistructuredReplyToBroker([prediction, MAE], body, "http://172.28.2.1:1026/v2/entities/Concrete/attrs/", "PATCH")
        print(response)
               
    return response


try:
   event, ssc = connector.Prime(sc, 1 , StorageLevel.MEMORY_AND_DISK_2)
   entity = event.flatMap(lambda x: x.entities)
   entity.foreachRDD(lambda rdd: rdd.foreachPartition(Predict))
except Exception as e:
    print(e)



ssc.start()
ssc.awaitTermination()

'''
while True:
    try:
        time.sleep(600)
    except Exception as e:
        #f.close()
        sys.exit(0)
'''

