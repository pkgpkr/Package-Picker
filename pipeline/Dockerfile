# Our version of PySpark requires Python 3.7
FROM python:3.7

ARG DB_USER
ARG DB_HOST
ARG DB_PASSWORD
ARG GITHUB_TOKEN
ARG MONTH

ENV PYTHONUNBUFFERED 1
ENV DB_USER $DB_USER
ENV DB_HOST $DB_HOST
ENV DB_PASSWORD $DB_PASSWORD
ENV GITHUB_TOKEN $GITHUB_TOKEN
ENV MONTH $MONTH

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/

# Our version of PySpark requires Java 8
RUN echo "deb http://ftp.us.debian.org/debian sid main" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get install openjdk-8-jdk -y
RUN pip install -r requirements.txt

COPY . /code/

RUN wget https://jdbc.postgresql.org/download/postgresql-42.2.11.jar

CMD python3 scraper/script.py && spark-submit --driver-class-path=postgresql-42.2.11.jar --jars=postgresql-42.2.11.jar model/generate.py

