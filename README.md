![ML Pipeline Tests](https://github.com/pkgpkr/Package-Picker/workflows/Scraper%20Test%20CI/badge.svg) ![ML Pipeline Deploy](https://github.com/pkgpkr/Package-Picker/workflows/Deploy%20ML%20Pipeline%20to%20Amazon%20ECS/badge.svg) ![Webserver Tests](https://github.com/pkgpkr/Package-Picker/workflows/Webserver%20Django%20CI/badge.svg) ![Webserver Deploy](https://github.com/pkgpkr/Package-Picker/workflows/Deploy%20to%20Amazon%20ECS/badge.svg)

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
AWS_ACCESS_KEY_ID.    # Your AWS account's access key
AWS_SECRET_ACCESS_KEY # Your AWS account's secret access key
CLIENT_ID             # ID of the GitHub app used by the web server
CLIENT_SECRET         # Secret for the GitHub app
DB_HOST               # Database URL
DB_PASSWORD           # Database password
DB_USER               # Database user
DOMAIN_NAME           # The domain name where the site is hosted (e.g. http://pkgpkr.com)
MONTH                 # How many months of data to scrape
SELENIUM_TEST         # Set if running Selenium tests
TOKEN                 # Your GitHub API token
```

# Run locally

NOTE: Before running any of the components, set the environment variables listed above and install Docker.

## Data scraper

1. Switch to the `pipeline/` folder and build the Docker image.

```
cd pipeline
docker build --build-arg TOKEN=$TOKEN --build-arg MONTH=$MONTH --build-arg DB_USER=$DB_USER --build-arg DB_HOST=$DB_HOST --build-arg=DB_PASSWORD=$DB_PASSWORD .
```

2. Run the Docker image. It will automatically scrape data and train the model, and quit when done.

`docker run -i -t <id>`

### Testing

Run this inside the `pipeline/` folder.

`DB_USER=$DB_USER DB_PASSWORD=$DB_PASSWORD DB_HOST=$DB_HOST TOKEN=$TOKEN python3 -m unittest scraper/test.py -v`

## Web server

1. Switch to the `webserver/pkgpkr/` folder and build the Docker image.

```
cd webserver/pkgpkr
docker build --build-arg DOMAIN_NAME=$DOMAIN_NAME --build-arg CLIENT_ID=$CLIENT_ID --build-arg CLIENT_SECRET=$CLIENT_SECRET --build-arg DB_USER=$DB_USER --build-arg DB_PASSWORD=$DB_PASSWORD --build-arg DB_HOST=$DB_HOST .
```

2. Run the Docker image (remember the `-p` flag to expose the webserver port)

`docker run -i -t -p 8000:80 <id>`

3. When the web server starts, open your browser to http://localhost:8000

### Testing

Run this inside the `webserver/pkgpkr` folder.

```
python3 manage.py collectstatic
SELENIUM_TEST=1 CLIENT_ID=$CLIENT_ID CLIENT_SECRET=$CLIENT_SECRET DB_HOST=$DB_HOST DB_USER=$DB_USER DB_PASSWORD=$DB_PASSWORD python3 manage.py test
```

# Run on AWS

Install Terraform and initialize it within the `terraform/` folder.

```
cd terraform
terraform init
```

## No custom domain

1. `terraform apply` (don't provide a value for `DOMAIN_NAME`)
2. Create a new GitHub OAuth application with a `http://<ELB DNS name>/callback` URL that maps to the load balancer DNS name that was just provisioned
3. Update your CLIENT_ID, CLIENT_SECRET, and DOMAIN_NAME secrets in GitHub
4. Commit the changes from step 1 to trigger a new image deployment
5. Open the load balancer DNS name in your browser

## pkgpkr.com domain only

1. `terraform apply` (provide `pkgpkr.com` for `DOMAIN_NAME`)
2. Update the `pkgpkr.com` and `*.pkgpkr.com` entries in the `pkgpkr.com` hosted zone to point at the ELB DNS name
3. Commit the changes from step 1 to trigger a new image deployment
4. Open pkgpkr.com in your web browser (it may take up to 5 minutes for the TTL on pkgpkr.com to expire)

# Pull Request

1. make your final commit for this branch
2. send a pull request from `your branch name` to `origin/dev`

# Merge

1. need at least one peer to review code and approve the change
2. let Jenkins build and check tests(including lint) and do the merge if no error
