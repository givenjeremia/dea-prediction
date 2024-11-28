FROM python:3.10-slim-bullseye

ENV APP_HOME=/app

WORKDIR $APP_HOME

RUN apt-get update && \
    apt-get install -y make && \
    apt-get clean

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip3 install -r requirements.txt

ADD . /app

COPY .env.example .env

RUN rm -rf /app/.git

EXPOSE 8080

CMD /app/bin/entrypoint.sh
