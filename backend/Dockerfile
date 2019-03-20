FROM python:3.7-alpine

LABEL Name=soarcast maintainer=thedingwing@gmail.com

ADD . /app
WORKDIR /app

RUN python3 -m pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy

EXPOSE 8000
CMD ["gunicorn"  , "-b", "0.0.0.0:8000", "app:app"]

