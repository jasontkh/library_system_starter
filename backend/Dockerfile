FROM python:alpine

WORKDIR /app

RUN apk add --no-cache linux-headers build-base

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["flask", "--app", "main", "run", "--host", "0.0.0.0"]

