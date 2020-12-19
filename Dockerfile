FROM python:3
EXPOSE 8089
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install uwsgi
RUN useradd -ms /bin/bash snakebin
RUN chown -R snakebin:users .
USER snakebin
ENV FLASK_APP=engine.py
RUN flask db upgrade
CMD uwsgi -M --socket 0.0.0.0:8089 --protocol=http --wsgi-file engine.py --callable app
