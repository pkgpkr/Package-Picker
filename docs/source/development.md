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
DB_USER=$DB_USER \
DB_PASSWORD=$DB_PASSWORD \
DB_HOST=$DB_HOST \
DB_PORT=$DB_PORT \
DB_DATABASE=$DB_DATABASE \
GH_TOKEN=$GH_TOKEN \
python3 -m unittest -v
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

SELENIUM_TEST=1 \
CLIENT_ID=$CLIENT_ID \
CLIENT_SECRET=$CLIENT_SECRET \
DB_HOST=$DB_HOST \
DB_PORT=$DB_PORT \
DB_DATABASE=$DB_DATABASE \
DB_USER=$DB_USER \
DB_PASSWORD=$DB_PASSWORD \
python3 manage.py test
```
