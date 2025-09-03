FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --cache-dir=/root/.cache/pip -r requirements.txt

COPY . .

EXPOSE 8000

ENV PYTHONPATH=/app

CMD ["uvicorn", "Src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app"]
