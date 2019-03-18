FROM python:3.7-alpine

LABEL Name=soarcast Version=0.0.1
EXPOSE 5000

WORKDIR /app
ADD . /app


RUN python3 -m pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy
CMD ["gunicorn"  , "-b", "0.0.0.0:5000", "app:app"]

