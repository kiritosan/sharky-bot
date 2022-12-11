FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

COPY requirements.txt /tmp
RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt

WORKDIR /app
COPY . .
