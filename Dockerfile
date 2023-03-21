FROM python:3.8-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -q -r requirements.txt

COPY ./docker/ /app/
RUN chmod +x /app/*

COPY . /app/

CMD [ "/app/webserver-start.sh" ]