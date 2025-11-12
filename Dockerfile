FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requires/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]