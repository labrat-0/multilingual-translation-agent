# 1. Use a stable, lightweight Python base
FROM python:3.12-slim

# 2. Set environment variables to ensure logs are visible and paths are correct
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/usr/src/app"

# 3. Set the working directory
WORKDIR /usr/src/app

# 4. Handle dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy your source code into the container
COPY . .

# 6. Start the agent
CMD ["python3", "-m", "src.agent.main"]
