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
coverage3 run --source scraper,model --omit "*/__init__.py,*/tests/*" -m unittest
coverage3 report -m
```

For more reports, may additionally run:

```
coverage3 html
```

and then open htmlcov/index.html or any other reports of interest.

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
coverage3 run --source webservice/ --omit "*/__init__.py,*/urls.py,*/apps.py,*/webservice/tests/*" ./manage.py test
coverage3 report -m
```

For more reports, may additionally run:

```
coverage3 html
```

and then open htmlcov/index.html or any other reports of interest.

## Docs

To build the docs, first install Sphinx. If on macOS, you can install via brew, so long as you add sphinx-doc to
your path afterwards:

```
brew install sphinx-doc
echo 'export PATH="/usr/local/opt/sphinx-doc/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Then switch to the `docs/` directory and build the docs. You may need to create a virtual environment first.

```
python3 -m venv docs_env
pip install -r requirements.txt
make html
```

Once the docs have built, you can view them (on macOS) with the following command.

```
open build/html/index.html
```

If you created a virtual environment, deactivate it and optionally delete the environment folder when done.

```
deactivate
rm -rf docs_env
```