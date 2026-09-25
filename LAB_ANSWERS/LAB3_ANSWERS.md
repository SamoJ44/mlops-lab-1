# Lab 3 Answers

## Question 1
My model was registered as **version 1**.

A logged model belongs to one MLflow run. A registered model gives the model a name and version so I can manage it separately from the run.

## Question 2
MLflow now uses **aliases** instead of the old stages like Staging and Production.

I used the alias **champion**. An alias is useful because I can move it to another model version without changing my code.

## Question 3
I load the model using:

`models:/food11@champion`

This is better than using a direct `.pth` path because my code does not depend on one local file. If I want to serve a newer model, I only move the `champion` alias to the new version.

## Question 4
I copy `pyproject.toml` and `uv.lock` before the source code so Docker can cache the dependency installation.

If I only change `serve.py`, Docker can reuse the dependency layer instead of installing everything again.

## Question 5
My multi-stage image was about **2.07 GB** disk usage and **441 MB** content size.

My naive single-stage image was about **2.22 GB** disk usage and **473 MB** content size.

So the multi-stage image saved about **150 MB** of disk usage.

The biggest layer was the virtual environment:
- Multi-stage `.venv` layer: about **1.49 GB**
- Naive `uv sync` layer: about **1.54 GB**

The naive image also kept the `uv` installation layer, about **63.8 MB**.

## Question 6
Without `.dockerignore`, Docker would send unnecessary files like the dataset, `.venv`, MLflow files, Git files, and cache files during the build.

This would make the build slower and use more space.

The local `.venv` could also cause problems if it was copied into the Linux container because my local environment was created on Windows.

## Question 7
`127.0.0.1` inside the container points to the container itself, not my Windows machine.

I used:

`host.docker.internal`

so the container could reach the MLflow server running on my host machine.

## Question 8
Yes. I stopped the container and started a new one from the same image without rebuilding.

The model loaded correctly again.

This shows that the code and dependencies are inside the Docker image, while the model is downloaded from MLflow when the container starts.

## Question 9
The Dockerfile is saved in Git, but the Docker image is still only on my computer.

To let another machine use the exact same image, I need to push it to a container registry such as Docker Hub or GHCR.

Using a fixed tag or image digest would make sure the same image is pulled.
