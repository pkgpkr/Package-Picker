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

    arguments:
        :cursor: Database cursor

    returns:
        Spark DataFrame
    """

    context = SparkContext("local[1]", "pkgpkr")

    # Load the raw data into Spark
    cursor.execute("SELECT * FROM dependencies")
    dependencies = cursor.fetchall()
    spark = SparkSession.builder.master("local[1]").appName("pkgpkr").getOrCreate()
    dataframe = spark.createDataFrame(dependencies).toDF("application_id", "package_id")

    # Restructure the dataframe in preparation for one-hot encoding
    grouped_dataframe = dataframe.groupBy("application_id").agg(collect_list("package_id"))
    grouped_dataframe = grouped_dataframe.withColumnRenamed("collect_list(package_id)", "package_ids")
    grouped_dataframe = grouped_dataframe.withColumn("package_ids", col("package_ids").cast("array<string>"))

    # One-hot encode the data (rows are applications, columns are packages)
    vectorizer = CountVectorizer(inputCol="package_ids", outputCol="packages_encoded")
    vectorizer_model = vectorizer.fit(grouped_dataframe)
    transformed_dataframe = vectorizer_model.transform(grouped_dataframe)
    transformed_dataframe = transformed_dataframe.drop(col("package_ids"))

    # Extract vectors from the DataFrame in preparation for computing the similarity matrix
    array = [Vectors.fromML(row.packages_encoded) for row in transformed_dataframe.collect()]

    # Create a RowMatrix
    matrix = RowMatrix(context.parallelize(array, numSlices=100))

    # Compute column similarity matrix
    similarity = matrix.columnSimilarities()

    # Convert the matrix to a DataFrame
    entries = similarity.entries.collect()
    similarity_dataframe = spark.createDataFrame(entries).toDF("a", "b", "similarity")

    # Map the package identifiers back to their pre-vectorized values
    mapping = create_map([lit(x) for x in chain(*enumerate(vectorizer_model.vocabulary))])
    similarity_dataframe = similarity_dataframe.withColumn("package_a", mapping.getItem(col("a")).cast("integer")) \
                                 .withColumn("package_b", mapping.getItem(col("b")).cast("integer"))
    similarity_dataframe = similarity_dataframe.drop(col("a")).drop(col("b"))

    # Mirror the columns and append to the existing dataframe so we need only query the first column
    similarity_dataframe = similarity_dataframe.select('package_a', 'package_b', 'similarity') \
                                 .union(similarity_dataframe.select('package_b', 'package_a', 'similarity'))

    # Add a column of zeros for bounded_similarity
    return similarity_dataframe.withColumn("bounded_similarity", lit(0))
    