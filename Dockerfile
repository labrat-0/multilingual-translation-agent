FROM apify/actor-python:latest

# Set src/ on the Python module search path
ENV PYTHONPATH=/usr/src/app/src

# Copy all files from the repo
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Default command to run your actor
CMD ["python", "src/agent/main.py"]
