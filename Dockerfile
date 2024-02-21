FROM python:3.10-slim
COPY . /app
RUN mkdir -p /app/storage
RUN touch /app/storage/data.json
WORKDIR /app
CMD ["python", "main.py"]
