FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the source code into the container
COPY src/ .

RUN pip install pyrofork google-generativeai pillow

# Command to run the bot
CMD ["python", "gemini.py"]