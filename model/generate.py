import os
import boto3
import glob
import psycopg2
from pyspark.mllib.linalg.distributed import RowMatrix
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.linalg import SparseVector
from pyspark.ml.feature import CountVectorizer
from pyspark.sql.functions import col
from pyspark.sql.functions import collect_list
from pyspark.sql.functions import lit
from pyspark.sql import Row

# Connect to the database
user = os.environ.get("DB_USER")
password = os.environ.get("DB_PASSWORD")
host = os.environ.get("DB_HOST")
db = psycopg2.connect(user=user, password=password, host=host)
cur = db.cursor()

# Load the raw data into Spark
cur.execute("SELECT * FROM dependencies")
dependencies = cur.fetchall()
spark = SparkSession.builder.appName("pkgpkr").getOrCreate()
df = spark.createDataFrame(dependencies).toDF("application_id", "package_id")

# Close the database connection
cur.close()
db.close()

# Restructure the dataframe in preparation for one-hot encoding
grouped = df.groupBy("application_id").agg(collect_list("package_id"))
grouped = grouped.withColumnRenamed("collect_list(package_id)", "package_ids")
grouped = grouped.withColumn("package_ids", col("package_ids").cast("array<string>"))

# One-hot encode the data (rows are applications, columns are packages)
vectorizer = CountVectorizer(inputCol="package_ids", outputCol="packages_encoded")
vectorizer_model = vectorizer.fit(grouped)
transformedDf = vectorizer_model.transform(grouped)
transformedDf = transformedDf.drop(col("package_ids"))

# Extract vectors from the DataFrame in preparation for computing the similarity matrix
array = [Vectors.fromML(row.packages_encoded) for row in transformedDf.collect()]

# Create a RowMatrix
matrix = RowMatrix(sc.parallelize(array))

# Compute column similarity matrix
similarity = matrix.columnSimilarities()

# Convert the matrix to a DataFrame
entries = similarity.entries.collect()
similarityDf = spark.createDataFrame(entries).toDF("package_a", "package_b", "similarity")

# Write to the database
url_connect = f"jdbc:postgresql://{host}/"
table = "similarity"
mode = "overwrite"
properties = {"user":user, "password":password, "driver":"org.postgresql.Driver"}
similarityDf.write.jdbc(url_connect, table, mode, properties)