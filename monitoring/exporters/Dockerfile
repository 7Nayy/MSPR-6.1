FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY wildaware_exporter.py .

EXPOSE 9090

CMD ["python", "wildaware_exporter.py"]
