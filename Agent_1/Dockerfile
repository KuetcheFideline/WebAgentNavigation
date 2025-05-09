FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install python3 gcc libc-dev -y \ 
    && apt-get install -y binutils

RUN pip install --upgrade pip 
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app

WORKDIR  /app
COPY ./Agent1 /app

EXPOSE 8000
ENTRYPOINT ["python","Task.py"]
