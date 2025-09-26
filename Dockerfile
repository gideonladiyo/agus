# Gunakan image Python minimal
FROM python:3.11-slim

# Install dependency sistem yang dibutuhkan
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory di dalam container
WORKDIR /app

# Salin requirements dan install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh isi project ke dalam container
COPY . /app/

# Jalankan aplikasi
CMD ["python", "bot.py"]