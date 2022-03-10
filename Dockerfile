FROM python:3.8-alpine

RUN mkdir yamtest && mkdir app
COPY requirements.txt yamtest
RUN pip install --no-cache-dir -r /yamtest/requirements.txt

COPY src /yamtest/src
COPY main.py /yamtest
WORKDIR app

CMD ["python", "/yamtest/main.py", "/app"]
