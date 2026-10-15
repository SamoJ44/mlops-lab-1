# Lab 4 — Docker Compose Questions

## Question 1
Without a volume, data saved in `/mlflow-data` belongs to that container. Removing it and creating a new container loses that data, so the new MLflow UI starts empty. I did not test this standalone case separately.

## Question 2
A named volume is managed by Docker and keeps MLflow data separate from the project files. A bind mount would also work, but I would have to manage the host folder and its permissions myself.

## Question 3
Docker Compose creates a shared network with DNS for service names. That is why `http://mlflow:5000` resolves inside the inference container, unlike in Lab 3 when MLflow was running on my host.

## Question 4
The environment variable makes the frontend reusable. In Compose, I set it to `http://inference:8000`; outside Compose, I can point it to another API address without changing the code.

## Question 5
Inference does not need a host-published port because only the frontend calls it. Streamlit reaches the API through the internal Compose network at `http://inference:8000`.

## Question 6
`depends_on` controls start order, not readiness. If MLflow is not ready when inference loads the model, inference can fail and exit. I can inspect this with `docker compose logs inference` and restart it once MLflow is ready.

## Question 7
MLflow publishes port `5000` and the frontend publishes `8501`. Inference only exposes `8000/tcp` internally. This matches my `docker-compose.yml`.

## Question 8
Changing the model alias does not update the model already loaded in FastAPI's memory. I moved my `champion` alias from version 2 to version 3, then used `docker compose restart inference` to load the current version. My project uses `champion` instead of `Staging`, and both versions referenced the same model artifacts, so I did not expect different predictions.

## Question 9
Restarting is enough because the Docker image contains the application code and dependencies, while FastAPI fetches the selected model from MLflow at startup. The image does not need to be rebuilt when the alias changes.

## Question 10
After `docker compose down` and `up`, my model and the `champion` alias (version 3) were still there because the named volume was preserved. After `docker compose down -v`, the volume was removed and recreated empty, so the model data was lost from that volume. I restored it from my backup and confirmed that version 3 was available again.

## Question 11
For three inference replicas behind a load balancer and recovery from a machine failure, I would need an orchestration platform such as Kubernetes, with replica management, health checks, load balancing, and persistent/shared storage. This basic Docker Compose setup does not provide multi-machine high availability.
