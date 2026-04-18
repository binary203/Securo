FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install semgrep

COPY . /app/

EXPOSE 5000

ENV FLASK_APP=start.py
ENV FLASK_CONFIG=production

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "start:app"]
