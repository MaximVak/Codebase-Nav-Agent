FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt

RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend
COPY sample_repo ./sample_repo
COPY README.md ./README.md
COPY LICENSE ./LICENSE

WORKDIR /app/backend

ENTRYPOINT ["python", "main.py"]