FROM python:3.9-slim

# Set the working directory
WORKDIR /app

RUN pip install pyrofork google-generativeai pillow

# Copy the source code into the container
COPY src/ .

# Command to run the bot
CMD ["python", "gemini.py"]