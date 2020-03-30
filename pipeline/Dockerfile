FROM python:3

ARG DB_USER
ARG DB_HOST
ARG DB_PASSWORD
ARG TOKEN
ARG MONTH

ENV PYTHONUNBUFFERED 1
ENV DB_USER $DB_USER
ENV DB_HOST $DB_HOST
ENV DB_PASSWORD $DB_PASSWORD
ENV TOKEN $TOKEN
ENV MONTH $MONTH

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/

RUN apt-get update
RUN apt-get install openjdk-11-jdk -y
RUN pip install -r requirements.txt

COPY . /code/

RUN wget https://jdbc.postgresql.org/download/postgresql-42.2.11.jar

CMD python3 scraper/Script.py && spark-submit --driver-class-path=postgresql-42.2.11.jar --jars=postgresql-42.2.11.jar model/generate.py

