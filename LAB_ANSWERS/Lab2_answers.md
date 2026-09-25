# Lab 2 - Answers

## Question 1
**Look at `pyproject.toml` and `uv.lock`. What changed?**

After running:

```bash
uv add mlflow torch torchvision scikit-learn
```

`pyproject.toml` was updated to include the new direct project dependencies: `mlflow`, `torch`, `torchvision`, and `scikit-learn`.

Because this project uses the CPU-only PyTorch build, `pyproject.toml` also contains the PyTorch CPU index and source configuration:

```toml
[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[tool.uv.sources]
torch = { index = "pytorch-cpu" }
torchvision = { index = "pytorch-cpu" }
```

`uv.lock` was also updated. It contains the exact resolved versions of the direct dependencies and all of their transitive dependencies, together with the information needed by `uv` to reproduce the same environment later.

---

## Question 2
**What is `--backend-store-uri` used for? What is `--default-artifact-root` used for? What is the difference between the metadata MLflow stores and the artifacts it stores?**

`--backend-store-uri sqlite:///mlflow.db` tells MLflow where to store tracking metadata. In this lab, that metadata is stored in the local SQLite database file `mlflow.db`.

The metadata includes information such as:
- experiment names
- run IDs
- run status
- parameters
- metric values
- timestamps
- artifact locations

`--default-artifact-root ./mlruns` tells MLflow where to store larger files produced by runs.

Artifacts can include:
- trained models
- plots
- images
- exported files
- other run outputs

The main difference is that metadata describes the run and its results, while artifacts are the actual files produced by the run.

---

## Question 3
**Why shouldn't `mlflow.db` and `mlruns/` be tracked by Git, and why shouldn't they be tracked by DVC either?**

`mlflow.db` and `mlruns/` are local experiment-tracking outputs rather than source code or source datasets.

They should not be tracked by Git because they can change after every training run, may become large, and would create unnecessary repository changes and merge conflicts.

They should not be tracked by DVC either because MLflow already manages experiment metadata and artifacts. DVC is used in this project to version datasets and data-related files, while MLflow is responsible for experiment tracking.

Therefore, these files are added to `.gitignore`:

```text
mlflow.db
mlruns/
```

---

## Question 4
**What happens the first time you call `set_experiment` with a name that doesn't exist yet?**

When:

```python
mlflow.set_experiment("food11")
```

is called and an experiment named `food11` does not already exist, MLflow automatically creates the experiment and makes it the active experiment.

The experiment then appears in the MLflow UI, and later runs are recorded inside the `food11` experiment instead of the `Default` experiment.

---

## Question 5
**What is the difference between `mlflow.log_param` and `mlflow.log_metric`? Why does `log_metric` take a `step` argument and `log_param` doesn't?**

`mlflow.log_param` is used for fixed configuration values chosen for a run, such as:

- learning rate
- batch size
- number of epochs
- dataset choice

For example:

```python
mlflow.log_param("lr", 0.001)
```

`mlflow.log_metric` is used for values measured during or after training, such as:

- training loss
- validation loss
- validation accuracy
- test accuracy

For example:

```python
mlflow.log_metric("val_accuracy", val_accuracy, step=epoch)
```

A metric can change over time, so the `step` argument tells MLflow at which epoch or training step that value was measured. This allows MLflow to plot the metric over time.

A parameter normally stays fixed during the whole run, so it does not need a `step`.

---

## Question 6
**Open the run in the MLflow UI. Find the params, the metric charts, and the logged model artifact. Where does the model artifact actually live on disk?**

The successful baseline run logged parameters such as:

- `dataset = mini`
- `epochs = 5`
- `lr = 0.001`
- `batch_size = 32`

It also logged:
- `train_loss`
- `val_loss`
- `val_accuracy`
- `test_accuracy`

The trained PyTorch model was stored as an MLflow model artifact.

For the successful run inspected during this lab, the model was stored at:

```text
mlruns/1/models/m-d02a086048f74f01996897f479bd2fb3/artifacts/data/model.pth
```

The full model artifact directory also contains files such as:

```text
MLmodel
conda.yaml
python_env.yaml
requirements.txt
data/model.pth
data/pickle_module_info.txt
```

---

## Question 7
**Which learning rate gave the best `val_accuracy`? Is higher always better?**

For the runs using batch size 32, the final validation accuracies were:

| Learning rate | Final validation accuracy |
|---:|---:|
| `0.01` | `0.1551` |
| `0.001` | `0.5356` |
| `0.0001` | `0.7974` |

Among the tested values, `0.0001` gave the best validation accuracy.

A higher learning rate was not better in these experiments. In particular, `0.01` performed poorly, while lowering the learning rate improved the final validation accuracy.

This conclusion applies only to the learning rates tested in this lab.

---

## Question 8
**Use the parallel coordinates plot to look at `lr`, `batch_size` and `val_accuracy` together. What pattern do you see?**

The runs produced the following results:

| Learning rate | Batch size | Final validation accuracy |
|---:|---:|---:|
| `0.01` | `32` | `0.1551` |
| `0.001` | `32` | `0.5356` |
| `0.0001` | `32` | `0.7974` |
| `0.001` | `64` | `0.6177` |

For batch size 32, lower learning rates were associated with higher validation accuracy in these runs.

At learning rate `0.001`, increasing the batch size from 32 to 64 also increased the final validation accuracy from `0.5356` to `0.6177`.

However, each configuration was only run once, and neural-network training is stochastic, so these results show a pattern in these experiments rather than a general rule.

---

## Question 9
**Sort the runs table by `val_accuracy` descending. Which run is the best one? Note its run ID.**

The run with the highest final validation accuracy was:

- Run name: `trusting-penguin-568`
- Learning rate: `0.0001`
- Batch size: `32`
- Final validation accuracy: `0.7974`
- Test accuracy: `0.8568`

Run ID:

```text
a49c04144efc4ec8b451255086fd8d48
```

This run ID should be kept for the next lab.
