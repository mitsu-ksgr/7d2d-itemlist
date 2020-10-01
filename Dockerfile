FROM python:3.8

ENV PYTHONUNBUFFERED 1

# for dev
ENV PYTHONDONTWRITEBYTECODE 1

RUN pip install --upgrade pip

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

