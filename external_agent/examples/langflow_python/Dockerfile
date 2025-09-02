FROM python:3.12-slim

WORKDIR /app

ENV GEMINI_API_KEY=SET_YOUR_VALUE

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
RUN ls -lasF /app/venv
COPY requirements.txt .

RUN /app/venv/bin/pip install uv
RUN /app/venv/bin/uv pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
