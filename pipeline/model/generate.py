"""
Train an item-to-item collaborative filtering model based on similarity matrices
"""

import os
import psycopg2
from pyspark.mllib.linalg.distributed import RowMatrix
from pyspark.mllib.linalg import Vectors
from pyspark.ml.feature import CountVectorizer
from pyspark.sql.functions import col
from pyspark.sql.functions import collect_list
from pyspark.sql import SparkSession
from pyspark import SparkContext
SC = SparkContext("local[2]", "pkgpkr")

# Connect to the database
USER = os.environ.get("DB_USER")
PASSWORD = os.environ.get("DB_PASSWORD")
HOST = os.environ.get("DB_HOST")
DB = psycopg2.connect(user=USER, password=PASSWORD, host=HOST)
CUR = DB.cursor()

# Load the raw data into Spark
CUR.execute("SELECT * FROM dependencies")
DEPENDENCIES = CUR.fetchall()
SPARK = SparkSession.builder.master("local[2]").appName("pkgpkr").getOrCreate()
DF = SPARK.createDataFrame(DEPENDENCIES).toDF("application_id", "package_id")

# Close the database connection
CUR.close()
DB.close()

# Restructure the dataframe in preparation for one-hot encoding
GROUPED = DF.groupBy("application_id").agg(collect_list("package_id"))
GROUPED = GROUPED.withColumnRenamed("collect_list(package_id)", "package_ids")
GROUPED = GROUPED.withColumn("package_ids", col("package_ids").cast("array<string>"))

# One-hot encode the data (rows are applications, columns are packages)
VECTORIZER = CountVectorizer(inputCol="package_ids", outputCol="packages_encoded")
VECTORIZER_MODEL = VECTORIZER.fit(GROUPED)
TRANSFORMED_DF = VECTORIZER_MODEL.transform(GROUPED)
TRANSFORMED_DF = TRANSFORMED_DF.drop(col("package_ids"))

# Extract vectors from the DataFrame in preparation for computing the similarity matrix
ARRAY = [Vectors.fromML(row.packages_encoded) for row in TRANSFORMED_DF.collect()]

# Create a RowMatrix
MATRIX = RowMatrix(SC.parallelize(ARRAY))

# Compute column similarity matrix
SIMILARITY = MATRIX.columnSimilarities()

# Convert the matrix to a DataFrame
ENTRIES = SIMILARITY.entries.collect()
SIMILARITY_DF = SPARK.createDataFrame(ENTRIES).toDF("package_a", "package_b", "similarity")

# Write to the database
URL_CONNECT = f"jdbc:postgresql://{HOST}/"
TABLE = "similarity"
MODE = "overwrite"
PROPERTIES = {"user": USER, "password": PASSWORD, "driver": "org.postgresql.Driver"}
SIMILARITY_DF.write.jdbc(URL_CONNECT, TABLE, MODE, PROPERTIES)
