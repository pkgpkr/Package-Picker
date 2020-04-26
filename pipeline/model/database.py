"""
Database processing to prepopulate UI tables
"""

def write_similarity_scores(scores, host, port, database, table, user, password):
    """
    Write similarity scores to the database
    :param scores: DataFrame containing pairs of packages and their similarity score
    :param host: Database host
    :param port: Database port
    :param database: Database name
    :param table: Database table for the similarity scores
    :param user: Database user
    :param password: Database password
    """

    connection_string = f"jdbc:postgresql://{host}:{port}/{database}"
    properties = {"user": user, "password": password, "driver": "org.postgresql.Driver"}
    scores.write.jdbc(connection_string, table, "overwrite", properties)

def update_bounded_similarity_scores(cursor):
    """
    Update bounded similarity score
    :param cursor: Database cursor
    """

    BOUNDED_SIMILARITY_UPDATE = """
    UPDATE similarity
    SET bounded_similarity = s.b_s
    FROM (
      SELECT package_a, package_b, WIDTH_BUCKET(similarity, 0, 1, 9) AS b_s
      FROM similarity
    ) s
    WHERE
    similarity.package_a = s.package_a
    AND
    similarity.package_b = s.package_b;
    """

    # Execute bounded similarity update
    cursor.execute(BOUNDED_SIMILARITY_UPDATE)

def update_popularity_scores(cursor):
    """
    Update popularity scores
    :param cursor: Database cursor
    """

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

    # Execute popularity updates
    cursor.execute(POPULARITY_UPDATE)
    cursor.execute(POPULARITY_NULL_TO_ZERO)
    cursor.execute(BOUNDED_POPULARITY_UPDATE)

def update_trending_scores(cursor):
    """
    Update trending scores
    :param cursor: Database cursor
    """

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
        LOG(monthly_downloads_last_month + 1) / (LOG(monthly_downloads_a_year_ago + 1) + 1),
        (SELECT MIN(LOG(monthly_downloads_last_month + 1) / (LOG(monthly_downloads_a_year_ago + 1) + 1)) FROM packages),
        (SELECT MAX(LOG(monthly_downloads_last_month + 1) / (LOG(monthly_downloads_a_year_ago + 1) + 1)) FROM packages),
        9
      ) AS relative_trend
      FROM packages
    ) s
    WHERE packages.id = s.id;
    """

    # Execute trending updates
    cursor.execute(MONTHLY_DOWNLOADS_LAST_MONTH_NULL_TO_ZERO)
    cursor.execute(MONTHLY_DOWNLOADS_A_YEAR_AGO_NULL_TO_ZERO)
    cursor.execute(ABSOLUTE_TREND_UPDATE)
    cursor.execute(RELATIVE_TREND_UPDATE)

def package_table_postprocessing(cursor):
    """
    Preprocessing on the packages table
    :param cursor: Database cursor
    """

    NPM_DEPENDENCY_BASE_URL = 'https://npmjs.com/package'
    
    SHORT_NAME_UPDATE = """
    UPDATE packages
    SET short_name = s.temp
    FROM (
      SELECT id, REGEXP_REPLACE(name, 'pkg:[^/]+/(.*)', '\\1') AS temp
      FROM packages
    ) s
    WHERE packages.id = s.id;
    """

    URL_UPDATE = f"""
    UPDATE packages
    SET url = s.temp
    FROM (
      SELECT id, CONCAT('{NPM_DEPENDENCY_BASE_URL}/', REGEXP_REPLACE(name, 'pkg:npm/(.*)@\\d+', '\\1')) AS temp
      FROM packages
    ) s
    WHERE packages.id = s.id;
    """

    DISPLAY_DATE_UPDATE = """
    UPDATE packages
    SET display_date = s.temp
    FROM (
      SELECT id, TO_CHAR(modified, 'yyyy-mm-dd') AS temp FROM packages
    ) s
    WHERE packages.id = s.id;
    """

    cursor.execute(SHORT_NAME_UPDATE)
    cursor.execute(URL_UPDATE)
    cursor.execute(DISPLAY_DATE_UPDATE)
