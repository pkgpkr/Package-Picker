# Local development

> NOTE: Before running any of the components, set the environment variables listed above and install Docker.

## Data scraper
### Run

1. Switch to the `pipeline/` folder and build the Docker image.

```
cd pipeline
docker build \
      --build-arg GH_TOKEN=$GH_TOKEN \
      --build-arg MONTH=$MONTH \
      --build-arg DB_USER=$DB_USER \
      --build-arg DB_HOST=$DB_HOST \
      --build-arg DB_PORT=$DB_PORT \
      --build-arg DB_DATABASE=$DB_DATABASE \
      --build-arg DB_PASSWORD=$DB_PASSWORD .
```

2. Run the Docker image. The image ID is shown after the Docker build successfully
   completes. It will automatically scrape data and train the model, and quit when done.

`docker run -i -t <id>`

### Test

Run this inside the `pipeline/` folder.

```
pip3 install -r requirements.txt
DB_USER=$DB_USER \
DB_PASSWORD=$DB_PASSWORD \
DB_HOST=$DB_HOST \
DB_PORT=$DB_PORT \
DB_DATABASE=$DB_DATABASE \
GH_TOKEN=$GH_TOKEN \
run coverage run --source scraper,model --omit */__init__.py,*/tests/* -m unittest
coverage html
open htmlcov/index.html
coverage report -m
```

## Web server
### Run
1. Switch to the `webserver/pkgpkr/` folder and build the Docker image.

```
cd webserver/pkgpkr
docker build \
      --build-arg DOMAIN_NAME=$DOMAIN_NAME \
      --build-arg CLIENT_ID=$CLIENT_ID \
      --build-arg CLIENT_SECRET=$CLIENT_SECRET \
      --build-arg DB_USER=$DB_USER \
      --build-arg DB_PORT=$DB_PORT \
      --build-arg DB_DATABASE=$DB_DATABASE \
      --build-arg DB_PASSWORD=$DB_PASSWORD \
      --build-arg DB_HOST=$DB_HOST .
```

2. Run the Docker image (remember the `-p` flag to expose the webserver port)

`docker run -i -t -p 8000:80 <id>`

3. When the web server starts, open your browser to http://localhost:8000

### Test

Run this inside the `webserver/pkgpkr` folder.

```
python3 manage.py collectstatic

pip3 install -r requirements.txt
SELENIUM_TEST=1 \
CLIENT_ID=$CLIENT_ID \
CLIENT_SECRET=$CLIENT_SECRET \
DB_HOST=$DB_HOST \
DB_PORT=$DB_PORT \
DB_DATABASE=$DB_DATABASE \
DB_USER=$DB_USER \
DB_PASSWORD=$DB_PASSWORD \
coverage run --source webservice/ --omit */__init__.py,*/urls.py,*/apps.py,*/webservice/tests/* ./manage.py test
coverage html
open htmlcov/index.html
coverage report -m
```
