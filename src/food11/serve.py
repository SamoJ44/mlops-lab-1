import io
import os

import mlflow
import numpy as np
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from torchvision import transforms


# ---------------------------------------------------------
# Class names
# ---------------------------------------------------------
CLASS_NAMES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]


# ---------------------------------------------------------
# MLflow configuration
# ---------------------------------------------------------
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


# ---------------------------------------------------------
# Load champion model once at startup
# ---------------------------------------------------------
MODEL_URI = "models:/food11@champion"

print(f"Loading model from {MODEL_URI}")
print(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")

model = mlflow.pyfunc.load_model(MODEL_URI)

print("Model loaded successfully")


# ---------------------------------------------------------
# Image preprocessing
# Must match training preprocessing
# ---------------------------------------------------------
transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------
app = FastAPI(
    title="Food-11 Classification API",
    version="1.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        image = Image.open(
            io.BytesIO(contents)
        ).convert("RGB")

    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid image",
        )

    # Preprocess image
    input_tensor = transform(image).unsqueeze(0)

    # MLflow PyFunc accepts NumPy tensor input
    predictions = model.predict(
        input_tensor.numpy()
    )

    # Convert model output logits to tensor
    logits = torch.as_tensor(
        np.asarray(predictions),
        dtype=torch.float32,
    )

    if logits.ndim == 1:
        logits = logits.unsqueeze(0)

    # Convert logits to probabilities
    probabilities = torch.softmax(
        logits,
        dim=1,
    )[0]

    predicted_index = int(
        torch.argmax(probabilities).item()
    )

    confidence = float(
        probabilities[predicted_index].item()
    )

    return {
        "category": CLASS_NAMES[predicted_index],
        "confidence": confidence,
    }