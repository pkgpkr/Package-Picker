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
from pyspark.sql import SparkSession
from pyspark import SparkContext
sc = SparkContext("local[2]", "pkgpkr")

# Connect to the database
user = os.environ.get("DB_USER")
password = os.environ.get("DB_PASSWORD")
host = os.environ.get("DB_HOST")
db = psycopg2.connect(user=user, password=password, host=host)
cur = db.cursor()

# Load the raw data into Spark
cur.execute("SELECT * FROM dependencies")
dependencies = cur.fetchall()
spark = SparkSession.builder.master("local[2]").appName("pkgpkr").getOrCreate()
df = spark.createDataFrame(dependencies).toDF("application_id", "package_id")

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

# Connect to S3
bucket = os.environ.get("S3_BUCKET")
path = os.environ.get("S3_MODEL_PATH")
access_key_id = os.environ.get("S3_ACCESS_KEY_ID")
secret_access_key = os.environ.get("S3_SECRET_ACCESS_KEY")
s3 = boto3.client('s3',
                  aws_access_key_id=access_key_id,
                  aws_secret_access_key=secret_access_key)

# Write the DataFrame to a Parquet file in preparation for upload
similarityDf.coalesce(1).write.format("parquet").option("compression", "gzip").option("header", "true").mode("overwrite").save(path.split('/')[-1])

# Upload the model file to S3
tempFile = glob.glob(path.split('/')[-1] + "/*.parquet")[0]
with open(tempFile, "r") as fileHandle:
    s3.put_object(Body=fileHandle, Bucket=bucket, Key=path)

# Close the database connection
cur.close()
db.close()