# Use a lightweight Python image
FROM python:3.11-slim

# Install system dependencies needed for sentencepiece/transformers
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src/app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Run the agent
CMD ["python3", "-m", "src.agent.main"]
