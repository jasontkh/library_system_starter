FROM python:3.10

RUN apt-get update && \
    apt-get install -yqq postgresql
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["flask", "--app", "main", "run", "--host", "0.0.0.0"]