from fpc import connector

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


###### CONNECTOR CONFIGURATION FOR MASTER - BEFORE STARTING #######
connector.RECV_SINGLETON.http_address = "172.28.1.1"
connector.RECV_SINGLETON.http_port = 8061
###########################################

def PrepareData(entity):
    # Function to prepare data for prediction.
    # It was adapted to prepare data from an NGSI Entity
    
    # Picking values from OCB, converting into "horizontal" numpy array
    values = np.array([val.value for val in entity.attrs.values()]).reshape(1, -1)
    # Creating a pandas dataframe to speed up data preparation
    df = pd.DataFrame(values, columns=list(entity.attrs.keys()))
    # Dropping target column and taking prediction single value
    x = df.drop('strength', axis=1).to_numpy().reshape(1,-1)
    y = df['strength'].to_numpy()
    return x, y


def PredictAndComputeError(x, y):
    # Function already built to predict data, left as is.
    
    prediction = loaded_model.predict(x)[0]
    # Computing absolute error between ground truth and predicted value
    MAE = np.abs(y - prediction)
    return prediction, MAE


def InjectAndPredict(iter):
    # Function injected into workers to work on RDDs
    
    ###### CONNECTOR CONFIGURATION INJECTION #######
    connector.REPL_SINGLETON.fiware_service = "tutorial"
    connector.REPL_SINGLETON.fiware_servicepath = "/pyspark"
    connector.REPL_SINGLETON.placeholder_string = "%%PLACEHOLDER%%"
    ###########################################

    # Iterating over entities (coming from flatmap)
    for entity in iter:
        
        x, y = PrepareData(entity)
        prediction, MAE = PredictAndComputeError(x, y)

        # Preparing body for request, sending to CB
        body = '''{"predicted_strength": {"value": %%PLACEHOLDER%% }, "prediction_error" : {"value": %%PLACEHOLDER%% }}'''
        response = connector.SemistructuredReplyToBroker([prediction, MAE], body, "http://172.28.2.1:1026/v2/entities/Concrete/attrs/", "PATCH")
        print(response)
    return response


try:
    event, ssc = connector.Prime(sc, 1 , StorageLevel.MEMORY_AND_DISK_2)
    entity = event.flatMap(lambda x: x.entities)
    entity.foreachRDD(lambda rdd: rdd.foreachPartition(InjectAndPredict))
except Exception as e:
    print(e)


# Run until killed
ssc.start()
ssc.awaitTermination()


