FROM python:3.7

ENV PORT 8085
ENV HOSTDIR 0.0.0.0

EXPOSE 8085

RUN apt-get update -y && \
    apt-get install -y python3-pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app


ENTRYPOINT ["python", "app.py"]
