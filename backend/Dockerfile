# 1. Use an official, lightweight Python image
FROM python:3.11-slim

# 2. Stop Python from generating .pyc files and force logs to stream immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Install system dependencies (needed for compiling certain ML/DB libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy your requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your backend code into the container
COPY . .

# 7. Expose the port FastAPI uses
EXPOSE 8000

# 8. The command to boot up the server when the container starts
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]