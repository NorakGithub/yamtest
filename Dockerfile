FROM python:3.8-alpine

COPY requirements.txt .
RUN mkdir yamls && pip install --no-cache-dir -r requirements.txt

COPY src src
COPY main.py .

CMD ["python", "main.py", "yamls"]
