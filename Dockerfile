FROM python:3.7-alpine

COPY ./requirements.txt /app/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN apk --update add libxml2-dev libxslt-dev libffi-dev libgcc openssl-dev curl
RUN apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev

RUN pip install -r requirements.txt

WORKDIR /app

COPY . /app/

EXPOSE 8000

# CMD python manage.py runserver 0.0.0.0:8000