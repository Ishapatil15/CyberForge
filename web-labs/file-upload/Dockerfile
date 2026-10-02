FROM python:3.12-slim
WORKDIR /app
RUN pip install fastapi uvicorn python-multipart
COPY app/ /app/
CMD ["python", "main.py"]
