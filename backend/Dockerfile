FROM python:3.12-slim

WORKDIR /app
RUN apt-get update \
  && apt-get install -y --no-install-recommends libglib2.0-0 libgomp1 \
  && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY policies ./policies
COPY data/calendar_events.example.json ./data/calendar_events.json

ENV APP_DATA_DIR=/app/data
ENV APP_POLICIES_DIR=/app/policies
EXPOSE 8080

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
