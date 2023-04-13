FROM python:alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["flask", "--app", "main", "--debug", "run"]