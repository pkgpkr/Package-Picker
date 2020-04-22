# Setup


## Set environment variables

```
AWS_ACCESS_KEY_ID     # Your AWS account's access key
AWS_SECRET_ACCESS_KEY # Your AWS account's secret access key
CLIENT_ID             # ID of the GitHub app used by the web server
CLIENT_SECRET         # Secret for the GitHub app
DB_HOST               # Database URL
DB_PASSWORD           # Database password
DB_USER               # Database user
DOMAIN_NAME           # The domain name where the site is hosted (e.g. https://pkgpkr.com)
MONTH                 # How many months of data to scrape
SELENIUM_TEST         # Set if running Selenium tests
GH_TOKEN              # Your GitHub API token
```

## Database

Terraform will provision a database for you (see the AWS section below), otherwise you will need to manually create a PostgreSQL instance in RDS.

> NOTE: Make sure the database is publicly accessible if you want to access it from your local developer setup.

### Load data

If you want to start with some data in the database so you don't have to run the ML pipeline first, run the following commands:

```
wget https://pkgpkr-models.s3.amazonaws.com/database.dump
psql -h <DB host> -U <DB user> <DB name> < database.dump
```

### Fresh start

If you want to populate the database with data from scratch, create new tables with the following SQL commands before running the ML pipeline:

```
CREATE TABLE applications (
  id SERIAL PRIMARY KEY,
  url TEXT NOT NULL,
  name TEXT NOT NULL,
  followers INTEGER,
  hash TEXT NOT NULL,
  retrieved TIMESTAMPTZ NOT NULL,
  CONSTRAINT unique_url UNIQUE (url)
);
CREATE TABLE packages (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  monthly_downloads_last_month INTEGER,
  monthly_downloads_a_year_ago INTEGER,
  absolute_trend INTEGER,
  relative_trend INTEGER,
  categories TEXT[],
  popularity INTEGER,
  bounded_popularity INTEGER,
  modified TIMESTAMPTZ,
  retrieved TIMESTAMPTZ NOT NULL
);
CREATE TABLE dependencies (
  application_id INTEGER REFERENCES applications (id),
  package_id INTEGER REFERENCES packages (id),
  CONSTRAINT unique_app_to_pkg UNIQUE (application_id, package_id)
);
CREATE TABLE similarity (
  package_a INTEGER REFERENCES packages (id),
  package_b INTEGER REFERENCES packages (id),
  similarity FLOAT(4) NOT NULL,
  CONSTRAINT unique_pkg_to_pkg UNIQUE (package_a, package_b)
);
```
