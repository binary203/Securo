FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y build-essential git && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y build-essential && apt-get autoremove -y
COPY . .

CMD ["python", "start.py"]
