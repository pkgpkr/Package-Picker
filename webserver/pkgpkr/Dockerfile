FROM python:3
ENV PYTHONUNBUFFERED 1
ENV DB_USER ${DB_USER}
ENV DB_PASSWORD ${DB_PASSWORD}
ENV DB_HOST ${DB_HOST}
ENV CLIENT_ID ${CLIENT_ID}
ENV CLIENT_SECRET ${CLIENT_SECRET}
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
EXPOSE 80
CMD python manage.py runserver 0.0.0.0:80
