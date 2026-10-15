
FROM python:3.11-slim

RUN pip install --no-cache-dir --timeout 300 --retries 10 mlflow

EXPOSE 5000



CMD ["mlflow", "server", \
     "--host", "0.0.0.0", "--port", "5000", \
     "--allowed-hosts", "mlflow:5000,localhost:*,127.0.0.1:*", \
     "--backend-store-uri", "sqlite:////mlflow-data/mlflow.db", \
     "--serve-artifacts", \
     "--artifacts-destination", "/mlflow-data/mlartifacts"]


