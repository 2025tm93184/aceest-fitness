FROM python:3.11-slim

WORKDIR /app

RUN useradd --create-home appuser
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY tests ./tests

USER appuser
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
