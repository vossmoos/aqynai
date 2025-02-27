FROM python:3.10-slim

WORKDIR /opt/dagster/app

COPY ./dag/ /opt/dagster/app/

RUN pip install -r requirements.txt

ENV DAGSTER_HOME=/opt/dagster/dagster_home

RUN mkdir -p $DAGSTER_HOME

# Copy dagster.yaml into $DAGSTER_HOME
COPY ./dag/dagster.yaml $DAGSTER_HOME
COPY ./dag/workspace.yaml $DAGSTER_HOME

EXPOSE 3000