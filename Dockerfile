FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY bot.py .
COPY image_generator.py .
COPY fonts/ ./fonts/

# Run the bot
CMD ["python", "bot.py"]
