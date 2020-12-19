FROM python:3

EXPOSE 8089

RUN pip install -r requirements.txt
RUN pip install uwsgi

COPY . /app
WORKDIR /app

RUN useradd -ms /bin/bash snakebin
RUN chown -R snakebin:users .
USER snakebin

ENV FLASK_APP=engine.py
RUN flask db upgrade
CMD uwsgi -M --socket 0.0.0.0:8089 --protocol=http --wsgi-file engine.py --callable app
