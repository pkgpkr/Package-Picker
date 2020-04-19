"""
Train an item-to-item collaborative filtering model based on similarity matrices
"""

import os
from itertools import chain
import psycopg2
from pyspark.mllib.linalg.distributed import RowMatrix
from pyspark.mllib.linalg import Vectors
from pyspark.ml.feature import CountVectorizer
from pyspark.sql.functions import col, collect_list, create_map, lit
from pyspark.sql import SparkSession
from pyspark import SparkContext

SC = SparkContext("local[1]", "pkgpkr")

# Connect to the database
USER = os.environ.get("DB_USER")
PASSWORD = os.environ.get("DB_PASSWORD")
HOST = os.environ.get("DB_HOST")
DB = psycopg2.connect(user=USER, password=PASSWORD, host=HOST)
CUR = DB.cursor()

# Load the raw data into Spark
CUR.execute("SELECT * FROM dependencies")
DEPENDENCIES = CUR.fetchall()
SPARK = SparkSession.builder.master("local[1]").appName("pkgpkr").getOrCreate()
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
MATRIX = RowMatrix(SC.parallelize(ARRAY, numSlices=50))

# Compute column similarity matrix
SIMILARITY = MATRIX.columnSimilarities()

# Convert the matrix to a DataFrame
ENTRIES = SIMILARITY.entries.collect()
SIMILARITY_DF = SPARK.createDataFrame(ENTRIES).toDF("a", "b", "similarity")

# Map the package identifiers back to their pre-vectorized values
MAPPING = create_map([lit(x) for x in chain(*enumerate(VECTORIZER_MODEL.vocabulary))])
SIMILARITY_DF = SIMILARITY_DF.withColumn("package_a", MAPPING.getItem(col("a")).cast("integer")) \
                             .withColumn("package_b", MAPPING.getItem(col("b")).cast("integer"))
SIMILARITY_DF = SIMILARITY_DF.drop(col("a")).drop(col("b"))

# Mirror the columns and append to the existing dataframe so we need only query the first column
SIMILARITY_DF = SIMILARITY_DF.select('package_a', 'package_b', 'similarity') \
                             .union(SIMILARITY_DF.select('package_b', 'package_a', 'similarity'))

# Write similarity scores to the database
URL_CONNECT = f"jdbc:postgresql://{HOST}/"
TABLE = "similarity"
MODE = "overwrite"
PROPERTIES = {"user": USER, "password": PASSWORD, "driver": "org.postgresql.Driver"}
SIMILARITY_DF.write.jdbc(URL_CONNECT, TABLE, MODE, PROPERTIES)

#
# Update popularity scores
#

POPULARITY_UPDATE = """
UPDATE packages
SET popularity = s.popularity
FROM (
  SELECT package_b, COUNT(package_b) AS popularity
  FROM similarity
  GROUP BY package_b
) s
WHERE packages.id = s.package_b;
"""

POPULARITY_NULL_TO_ZERO = """
UPDATE packages
SET popularity = 0
WHERE popularity IS NULL;
"""

BOUNDED_POPULARITY_UPDATE = """
UPDATE packages
SET bounded_popularity = s.popularity
FROM (
  SELECT id, WIDTH_BUCKET(LOG(popularity + 1), 0, (SELECT MAX(LOG(popularity + 1)) FROM packages), 9) AS popularity
  FROM packages
) s
WHERE packages.id = s.id;
"""

# Connect to the database
DB = psycopg2.connect(user=USER, password=PASSWORD, host=HOST)
CUR = DB.cursor()

# Execute popularity updates
CUR.execute(POPULARITY_UPDATE)
CUR.execute(POPULARITY_NULL_TO_ZERO)
CUR.execute(BOUNDED_POPULARITY_UPDATE)

#
# Update trending scores
#

MONTHLY_DOWNLOADS_LAST_MONTH_NULL_TO_ZERO = """
UPDATE packages
SET monthly_downloads_last_month = 0
WHERE monthly_downloads_last_month IS NULL;
"""

MONTHLY_DOWNLOADS_A_YEAR_AGO_NULL_TO_ZERO = """
UPDATE packages
SET monthly_downloads_a_year_ago = 0
WHERE monthly_downloads_a_year_ago IS NULL;
"""

ABSOLUTE_TREND_UPDATE = """
UPDATE packages
SET absolute_trend = s.absolute_trend
FROM (
  SELECT id, WIDTH_BUCKET(
    LOG(monthly_downloads_last_month + 1) - LOG(monthly_downloads_a_year_ago + 1),
    (SELECT MIN(LOG(monthly_downloads_last_month + 1) - LOG(monthly_downloads_a_year_ago + 1)) FROM packages),
    (SELECT MAX(LOG(monthly_downloads_last_month + 1) - LOG(monthly_downloads_a_year_ago + 1)) FROM packages),
    9
  ) AS absolute_trend
  FROM packages
) s
WHERE packages.id = s.id;
"""

RELATIVE_TREND_UPDATE = """
UPDATE packages
SET relative_trend = s.relative_trend
FROM (
  SELECT id, WIDTH_BUCKET(
    LOG((monthly_downloads_last_month / (monthly_downloads_a_year_ago + 1)) + 1),
    (SELECT MIN(LOG((monthly_downloads_last_month / (monthly_downloads_a_year_ago + 1)) + 1)) FROM packages),
    (SELECT MAX(LOG((monthly_downloads_last_month / (monthly_downloads_a_year_ago + 1)) + 1)) FROM packages),
    9
  ) AS relative_trend
  FROM packages
) s
WHERE packages.id = s.id;
"""

# Execute trending updates
CUR.execute(MONTHLY_DOWNLOADS_LAST_MONTH_NULL_TO_ZERO)
CUR.execute(MONTHLY_DOWNLOADS_A_YEAR_AGO_NULL_TO_ZERO)
CUR.execute(ABSOLUTE_TREND_UPDATE)
CUR.execute(RELATIVE_TREND_UPDATE)

# Commit changes and close the database connection
DB.commit()
CUR.close()
DB.close()
