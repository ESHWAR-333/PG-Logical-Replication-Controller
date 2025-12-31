FROM python:3.11-slim

WORKDIR /app

RUN pip install psycopg2-binary pyyaml

CMD ["python", "main.py"]
