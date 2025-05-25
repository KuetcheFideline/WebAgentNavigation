FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set DNS for build


RUN apt-get update && apt-get install -y python3 gcc libc-dev binutils

RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./Agent1 /app

EXPOSE 8000
ENTRYPOINT ["python", "Task.py"]