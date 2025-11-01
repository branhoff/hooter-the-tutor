FROM python:3.11-bookworm

WORKDIR /app

COPY requires/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["/bin/bash"]