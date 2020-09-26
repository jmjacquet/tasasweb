FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
# Install requirements
RUN pip install --upgrade pip
RUN pip install -r /code/requirements.txt
COPY . /code/
RUN apt-get update && apt-get install mc -y && apt-get install vim -y



