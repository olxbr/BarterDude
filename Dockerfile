FROM python:3.7-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=/app

RUN pip3 install --upgrade pip && rm -r ~/.cache/pip/

COPY ./requirements /app/requirements
RUN pip3 install \
    -r ./requirements/requirements_base.txt \
    -r ./requirements/requirements_test.txt \
    -r ./requirements/requirements_prometheus.txt \
    && rm -r ~/.cache/pip/

COPY . /app
RUN pip3 install -e .