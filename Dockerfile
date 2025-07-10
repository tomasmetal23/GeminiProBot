###################  builder  ###################
FROM python:3.11-slim AS builder
WORKDIR /install

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev       \
    && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

###################  runtime  ###################
FROM python:3.11-slim
WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
        libffi7         \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY src .

CMD ["python", "gemini.py"]
