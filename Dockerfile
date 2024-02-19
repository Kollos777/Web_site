FROM python:3.10-slim
COPY . .
RUN mkdir -p /app/storage
RUN touch /app/storage/data.json
WORKDIR /app
CMD ["python", "main.py"]
