"""
Train an item-to-item collaborative filtering model based on similarity matrices
"""

from itertools import chain
from pyspark.mllib.linalg.distributed import RowMatrix
from pyspark.mllib.linalg import Vectors
from pyspark.ml.feature import CountVectorizer
from pyspark.sql.functions import col, collect_list, create_map, lit
from pyspark.sql import SparkSession
from pyspark import SparkContext

def get_similarity_dataframe(cursor):
    """
    Compute a similarity matrix from the dependency table
    :param cursor: Database cursor
    :return: Spark DataFrame
    """

    SC = SparkContext("local[1]", "pkgpkr")

    # Load the raw data into Spark
    cursor.execute("SELECT * FROM dependencies")
    DEPENDENCIES = cursor.fetchall()
    SPARK = SparkSession.builder.master("local[1]").appName("pkgpkr").getOrCreate()
    DF = SPARK.createDataFrame(DEPENDENCIES).toDF("application_id", "package_id")

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
    MATRIX = RowMatrix(SC.parallelize(ARRAY, numSlices=100))

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

    # Add a column of zeros for bounded_similarity
    return SIMILARITY_DF.withColumn("bounded_similarity", lit(0))
    