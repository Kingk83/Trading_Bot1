FROM python:3.11-slim

WORKDIR /app

COPY trading_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY trading_bot/ ./

CMD ["python", "main.py"]
