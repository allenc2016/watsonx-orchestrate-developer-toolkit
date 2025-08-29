FROM python:3.12-slim

WORKDIR /app

ENV GEMINI_API_KEY=SET_YOUR_VALUE

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]