FROM python:3.9-alpine

WORKDIR /app

# Instala dependencias del sistema necesarias para pillow y pyrofork
RUN apk add --no-cache gcc musl-dev libffi-dev jpeg-dev zlib-dev

COPY src/ .

RUN pip install --no-cache-dir pyrofork google-generativeai pillow

CMD ["python", "gemini.py"]