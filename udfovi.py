from pyspark.sql import SparkSession
from pyspark.sql.functions import udf

import json
import numpy as np
import pandas as pd
import time
import pybaselines

### IMPORTING FILES
import conf as connectorconf
import connector_start.py



spark = SparkSession.builder.appName('CPS1 Streaming Kafka').master("yarn").getOrCreate()
# sc = spark.sparkContext
spark.sparkContext.setLogLevel("ERROR")
# ssc = StreamingContext(sc, 20)

KAFKA_BOOTSTRAP_SERVERS_CONS="kafka:9092"

###### Preparation read from HDFS
print("Started with Configuration")
data_path = 'hdfs://master:9000/user/hdfs/jobs/A3_EXE_CPS1_20220204/model/Workset_Statistics_M13.xlsx'
avg_spec = pd.read_excel(data_path, sheet_name="SIMCA", usecols="D", skipfooter=1)
# read average API concentration, model coefficients, wl start/end, and run settings
data_path = 'hdfs://master:9000/user/hdfs/jobs/A3_EXE_CPS1_20220204/model/General_List_M13.xlsx'
coeff_data = pd.read_excel(data_path, sheet_name="SIMCA", usecols="E")

coeff_data.rename(columns={coeff_data.columns[0]: "coeffs"}, inplace = True)
  
avg_api = coeff_data.values[0][0]
if type(avg_api) is not np.float64:
    avg_api = float(avg_api.replace(',','.'))
        
pls_coeff = coeff_data.iloc[1:]
print("Configuration completed")
########### end preparation


### Commenting the Kafka stream part 
#df = spark \
#    .readStream \
#    .format("kafka") \
#    .option("kafka.bootstrap.servers", "kafka:9092") \
#    .option("subscribe", "my-topic") \
#    .load() \
#    .selectExpr("CAST(value AS STRING)")

### ADDING PYSPARK STREAMING CONTEXT
ssc = spark.StreamingContext(spark.SparkContext(), 10)
df = ssc.socketTextStream(connectorconf.SOCKETADDRESS, connectorconf.SOCKETPORT, storageLevel=StorageLevel.MEMORY_AND_DISK_2)


def datachange_notification(val):
    print("New data change event", time.strftime("%a, %d %b %Y %H:%M:%S"))
    specarr = np.array(val)
    bkg = pybaselines.whittaker.asls(specarr, lam=1e7, p=0.02)[0]
    spectra_cor=np.array(specarr-bkg)
    spectra_cor_std=spectra_cor.std()
    spectra_cor_std = max(spectra_cor_std, 1e-16)
    processed_spectra = (spectra_cor-spectra_cor.mean())/spectra_cor.std()
    spectra_diff_from_avg = processed_spectra - avg_spec['Mean'].values
    c_pls = float(spectra_diff_from_avg @ pls_coeff.values) + avg_api
    print("API concentration is " + str(c_pls) + "%")
    return str(c_pls)

def Converter(str):
    json_object = json.loads(str)
    result = json_object['data'][0]['2:Ramanspectrum']['value']
    ramenSpectrum = np.asfarray(result.split(","), dtype = float)
    return datachange_notification(ramenSpectrum)

###Commenting this line
#NumberUDF = udf(lambda m: Converter(m))

NumberUDF = df.map(lambda x: Converter(x)) \



#write to console for debugging purpose
# query = df.withColumn("Concentration", NumberUDF("value")).select("Concentration").writeStream \
#     .format("console") \
#     .outputMode("append") \
#     .option("truncate", True) \
#     .start()

query = df.withColumn("Concentration", NumberUDF("value")) \
        .select("Concentration") \
        .selectExpr("CAST('Concentration' AS STRING)", "to_json(struct(*)) AS value") \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("topic", "spark.out") \
        .option("checkpointLocation", "./testdir") \
        .option("truncate", True) \
        .start()

query.awaitTermination()
