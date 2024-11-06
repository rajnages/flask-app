FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY app.py .
COPY templates/ ./templates/
COPY static/ ./static/

EXPOSE 5000

CMD ["python", "app.py"]