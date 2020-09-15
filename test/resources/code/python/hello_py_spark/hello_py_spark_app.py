import argparse
import time

# Import local module to test spark-submit--py-files dependencies
import hello_py_spark_udfs as udfs
from pyspark.ml import Pipeline  # importing to test mllib DLLs like liblapack.so
from pyspark.sql import SparkSession, SQLContext
from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType

if __name__ == "__main__":
    print("Hello World, this is PySpark!")

    parser = argparse.ArgumentParser(description="inputs and outputs")
    parser.add_argument("--input", type=str, help="path to input data")
    parser.add_argument("--output", required=False, type=str, help="path to output data")
    args = parser.parse_args()
    spark = SparkSession.builder.appName("SparkContainerTestApp").getOrCreate()
    sqlContext = SQLContext(spark.sparkContext)

    # Load test data set
    inputPath = args.input
    salesDF = spark.read.json(inputPath)
    salesDF.printSchema()

    salesDF.createOrReplaceTempView("sales")
    topDF = spark.sql("SELECT date, sale FROM sales WHERE sale > 750")
    # Show the first 20 rows of the dataframe
    topDF.show()
    time.sleep(60)

    # Calculate average sales by date
    averageSalesPerDay = salesDF.groupBy("date").avg().collect()
    print(averageSalesPerDay)

    outputPath = args.output

    # Define a UDF that doubles an integer column
    # The UDF function is imported from local module to test spark-submit--py-files dependencies
    double_udf_int = udf(udfs.double_x, IntegerType())

    # Save transformed data set to disk
    salesDF.select("date", "sale", double_udf_int("sale").alias("sale_double")).write.json(outputPath)