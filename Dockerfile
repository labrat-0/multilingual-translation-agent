# 1. Use a stable, lightweight Python base
FROM python:3.11-slim

# 2. Set environment variables to ensure logs are visible and paths are correct
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/usr/src/app"

# 3. Install system dependencies
# These are MANDATORY for building sentencepiece and sacremoses from source
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Set the working directory
WORKDIR /usr/src/app

# 5. Handle dependencies
COPY requirements.txt ./

# CRITICAL: We install the CPU-only version of Torch. 
# The standard version is 2GB+ (includes GPU drivers) which will fail on free-tier builds.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# 6. Copy your source code into the container
COPY . .

# 7. Start the agent
# Using the -m flag ensures that 'src.agent.main' is treated as a module,
# allowing it to find 'translator.py' correctly.
CMD ["python3", "-m", "src.agent.main"]
