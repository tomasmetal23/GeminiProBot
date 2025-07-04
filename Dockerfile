FROM python:3.9-slim

# Set the working directory
WORKDIR /app

RUN pip install pyrofork google-generativeai pillow

# Copy the source code into the container
COPY src/ .

# Create a non-root user and switch to it :D
RUN useradd -m geminiuser
RUN chown -R geminiuser:geminiuser /app
USER geminiuser

# Command to run the bot
CMD ["python", "gemini.py"]