FROM python:3.11

WORKDIR /app

COPY requires/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5100

CMD ["python", "main.py"]