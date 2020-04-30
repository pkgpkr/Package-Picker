# Our version of PySpark requires Python 3.7
FROM djsauble/pyspark-tiny:latest

# Activate Python 3.7
ARG PYTHON_VERSION='3.7.0'
ARG PYENV_HOME=/root/.pyenv
ENV PATH $PYENV_HOME/shims:$PYENV_HOME/bin:$PATH

# Read build-time arguments
ARG DB_USER
ARG DB_HOST
ARG DB_PORT
ARG DB_DATABASE
ARG DB_PASSWORD
ARG GH_TOKEN
ARG MONTH

# Set project-specific environment variables
ENV PYTHONUNBUFFERED 1
ENV DB_USER $DB_USER
ENV DB_HOST $DB_HOST
ENV DB_PORT $DB_PORT
ENV DB_DATABASE $DB_DATABASE
ENV DB_PASSWORD $DB_PASSWORD
ENV GH_TOKEN $GH_TOKEN
ENV MONTH $MONTH

# Setup code
WORKDIR /code
COPY . /code/
RUN pip install -r requirements.txt

CMD python3 run_scraper.py && spark-submit --driver-class-path=postgresql-42.2.11.jar --jars=postgresql-42.2.11.jar --driver-memory 12g train_model.py

