![Pipeline Tests](https://github.com/pkgpkr/Package-Picker/workflows/Scraper%20Test%20CI/badge.svg) ![Pipeline Deploy](https://github.com/pkgpkr/Package-Picker/workflows/Pipeline%20Deploy/badge.svg) ![Web Server Tests](https://github.com/pkgpkr/Package-Picker/workflows/Web%20Server%20Tests/badge.svg) ![Web Server Deploy](https://github.com/pkgpkr/Package-Picker/workflows/Web%20Server%20Deploy/badge.svg)

# Intro

Package Picker is a recommendation platform for JavaScript packages. It uses machine learning to predict packages that are frequently used with the packages in your projects. Check it out at [pkgpkr.com](http://pkgpkr.com).

# Get the code

NOTE: If you do not know the git CLI commands, recommend to use [sourcetree](https://www.sourcetreeapp.com/) or [gitkraren](https://www.gitkraken.com/).

1. git clone https://github.com/pkgpkr/Package-Picker.git to your local folder 
2. create a branch locally for your small features.
3. start coding.
4. make commits frequently

# Set environment variables

```
AWS_ACCESS_KEY_ID     # Your AWS account's access key
AWS_SECRET_ACCESS_KEY # Your AWS account's secret access key
CLIENT_ID             # ID of the GitHub app used by the web server
CLIENT_SECRET         # Secret for the GitHub app
DB_HOST               # Database URL
DB_PASSWORD           # Database password
DB_USER               # Database user
DOMAIN_NAME           # The domain name where the site is hosted (e.g. http://pkgpkr.com)
MONTH                 # How many months of data to scrape
SELENIUM_TEST         # Set if running Selenium tests
GITHUB_TOKEN                 # Your GitHub API token
```

# Database

Terraform will provision a database for you (see the AWS section below), otherwise you will need to manually create a PostgreSQL instance in RDS.

> NOTE: Make sure the database is publically accessible if you want to access it from your local developer setup.

## Load data

If you want to start with some data in the database so you don't have to run the ML pipeline first, run the following commands:

```
wget https://pkgpkr-models.s3.amazonaws.com/database.dump
psql -h <DB host> -U <DB user> <DB name> < database.dump
```

## Fresh start

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
  downloads_last_month INTEGER,
  categories TEXT[],
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

# Run

## Local development

> NOTE: Before running any of the components, set the environment variables listed above and install Docker.

### Data scraper

1. Switch to the `pipeline/` folder and build the Docker image.

```
cd pipeline
docker build --build-arg GITHUB_TOKEN=$GITHUB_TOKEN --build-arg MONTH=$MONTH --build-arg DB_USER=$DB_USER --build-arg DB_HOST=$DB_HOST --build-arg=DB_PASSWORD=$DB_PASSWORD .
```

2. Run the Docker image. It will automatically scrape data and train the model, and quit when done.

`docker run -i -t <id>`

#### Testing

Run this inside the `pipeline/` folder.

`DB_USER=$DB_USER DB_PASSWORD=$DB_PASSWORD DB_HOST=$DB_HOST GITHUB_TOKEN=$GITHUB_TOKEN python3 -m unittest scraper/test.py -v`

### Web server

1. Switch to the `webserver/pkgpkr/` folder and build the Docker image.

```
cd webserver/pkgpkr
docker build --build-arg DOMAIN_NAME=$DOMAIN_NAME --build-arg CLIENT_ID=$CLIENT_ID --build-arg CLIENT_SECRET=$CLIENT_SECRET --build-arg DB_USER=$DB_USER --build-arg DB_PASSWORD=$DB_PASSWORD --build-arg DB_HOST=$DB_HOST .
```

2. Run the Docker image (remember the `-p` flag to expose the webserver port)

`docker run -i -t -p 8000:80 <id>`

3. When the web server starts, open your browser to http://localhost:8000

#### Testing

Run this inside the `webserver/pkgpkr` folder.

```
python3 manage.py collectstatic
SELENIUM_TEST=1 CLIENT_ID=$CLIENT_ID CLIENT_SECRET=$CLIENT_SECRET DB_HOST=$DB_HOST DB_USER=$DB_USER DB_PASSWORD=$DB_PASSWORD python3 manage.py test
```

## AWS

Check out a new branch

```
git checkout -b deploy_to_aws
```

Install Terraform and initialize it within the `terraform/` folder.

```
cd terraform
terraform init
```

You'll also need to have the AWS CLI installed and configured.

```
aws configure
```

### No custom domain

1. `terraform apply`
    1. Don't provide a value for `DOMAIN_NAME`, just hit 'enter'
    2. `DB_PASSWORD` is the desired password for your database
    3. `DB_USER` is the desired username for your database
2. Create a new GitHub OAuth application
    1. Homepage URL is `http://<ELB DNS name>`
    2. Callback URL is `http://<ELB DNS name>/callback`
3. Set up the database (choose one)
    1. Load data into your databse (see "Database" section above)
    2. Start fresh by creating new tables (see "Database" section above)
4. Make sure all environment variables are set as secrets on your GitHub repository (see "Set environment variables" section above)
5. Commit the changes from step 1 and merge your branch to `dev` to trigger the deploy to AWS
6. After the GitHub deploy actions are complete, open the load balancer DNS name in your browser

### pkgpkr.com domain only

1. `terraform apply`
    1. Provide `pkgpkr.com` for `DOMAIN_NAME`
    2. `DB_PASSWORD` is the desired password for your database
    3. `DB_USER` is the desired username for your database
2. Update the `pkgpkr.com` and `*.pkgpkr.com` entries in the `pkgpkr.com` hosted zone to point at the ELB DNS name
3. Set up the database (choose one)
    1. Load data into your databse (see "Database" section above)
    2. Start fresh by creating new tables (see "Database" section above)
4. Make sure all environment variables are set as secrets on your GitHub repository (see "Set environment variables" section above)
5. Commit the changes from step 1 and merge your branch to `dev` to trigger the deploy to AWS
6. After the GitHub deploy actions are complete, open pkgpkr.com in your web browser (it may take up to 5 minutes for the TTL on pkgpkr.com to expire)

# Pull Request

1. make your final commit for this branch
2. send a pull request from `your branch name` to `origin/dev`

# Merge

1. need at least one peer to review code and approve the change
2. let Jenkins build and check tests(including lint) and do the merge if no error
