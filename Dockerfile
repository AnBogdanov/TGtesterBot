FROM python:3.8

WORKDIR /app

COPY . .

RUN apt-get update
RUN pip install -U pip
RUN pip install -r requirements.txt;

CMD python3 -m phone_get.py