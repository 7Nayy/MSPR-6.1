FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=python_file/app.py
ENV PYTHONPATH=/app

CMD ["python", "python_file/app.py"]
