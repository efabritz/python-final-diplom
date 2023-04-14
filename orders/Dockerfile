FROM python:3

COPY ./requirements.txt /src/requirements.txt

ENV PIP_ROOT_USER_ACTION=ignore
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR src
COPY . /src
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt