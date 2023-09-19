FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
# Declare build arguments
ARG OPENAI_API_KEY
ARG SERPAPI_API_KEY
ARG BROKER_URL

# Set environment variables from build arguments
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV SERPAPI_API_KEY=$SERPAPI_API_KEY
ENV BROKER_URL=$BROKER_URL

WORKDIR /app/
COPY requirements.txt requirements.txt
COPY . /app/
