FROM python:3.7-alpine

LABEL Name=soarcast Version=0.0.1
LABEL maintainer=thedingwing@gmail.com

ADD . /app
WORKDIR /app

RUN python3 -m pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy

EXPOSE 5000
CMD ["gunicorn"  , "-b", "0.0.0.0:5000", "app:app"]

