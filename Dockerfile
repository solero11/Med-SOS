FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY templates ./templates
COPY static ./static
COPY updates ./updates
RUN useradd -m appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "src.orchestrator.app:create_app", "--host", "0.0.0.0", "--port", "8000"]
