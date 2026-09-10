# Lab 1

## Question 1 — What do the files created by `uv init` contain?

Running `uv init` creates the basic structure of a Python project.

- **`pyproject.toml`** contains the project metadata, Python requirements, dependencies, and project configuration. Later, when Pillow was added using `uv add pillow`, it was recorded there.
- **`.python-version`** specifies the Python version used by the project.
- **`README.md`** is the initial project documentation file.
- **`src/mlops_lab_1/__init__.py`** initializes the Python package created by `uv`.

After dependencies are resolved, **`uv.lock`** is generated. It records the resolved dependency versions so the environment can be reproduced consistently.

In simple terms, `uv init` creates an organized and reproducible Python project structure.

---

## Question 2 — What files are created by `dvc init` and what should be pushed?

Running `dvc init` initializes DVC inside the Git repository.

Important DVC files include:

- **`.dvc/config`** — contains project-level DVC configuration, such as the default remote.
- **`.dvc/.gitignore`** — prevents DVC's internal local files from being committed.
- **`.dvcignore`** — allows files or directories to be excluded from DVC operations.

DVC also uses local cache and temporary storage internally for the actual data objects.

The small DVC configuration and metadata files should be committed to Git when appropriate.

The actual DVC cache, temporary files, datasets, credentials, and other large local data should not be committed to Git.

In simple terms, Git stores the small configuration and pointer files, while DVC manages the actual dataset contents.

---

## Question 3 — Where are the credentials stored, and should they be pushed?

For this lab, the DagsHub authentication settings were configured using the `--global` option.

The remote was configured with:

- authentication type: basic
- username: `SamoJ44`
- password: DagsHub access token

Because `--global` was used, these credentials are stored in DVC's user-level configuration outside the Git repository.

They should **never** be pushed to GitHub.

The repository can contain non-secret information such as the DVC remote URL and default remote name, but passwords and access tokens must remain outside Git.

---

## Question 4 — What happened to `.gitignore`?

When a directory is tracked using DVC, DVC updates `.gitignore` so Git does not directly track the actual data files.

In this lab, the large raw Food-11 dataset was deliberately kept local and ignored by Git.

The DVC-managed sample and processed dataset directories were also excluded from normal Git tracking, while their `.dvc` pointer files were committed.

This prevents large binary datasets from accidentally being added to Git history.

In simple terms, DVC tracks the data while Git is told not to track the actual image files.

---

## Question 5 — What is the `.dvc` file?

A `.dvc` file is a small metadata or pointer file representing data managed by DVC.

In this project, the DVC pointer files include:

- `data_sample.dvc`
- `data/food11_processed.dvc`
- `data/food11_processed_mini.dvc`

A `.dvc` file contains information such as:

- a hash identifying the data contents
- total size
- number of files for directory outputs
- path of the tracked data

The actual images are not stored inside the `.dvc` file.

Git commits the small `.dvc` pointer, while DVC stores the actual data in its cache and remote storage.

This allows a Git commit to identify exactly which version of the data belongs to that version of the project.

---

## Question 6 — GitHub Main Branch / DagsHub

### Is the code on GitHub?

Yes.

The GitHub repository contains the project source and configuration files required for the lab, including:

- `pyproject.toml`
- `uv.lock`
- `src/food11/data.py`
- `src/mlops_lab_1/__init__.py`
- DVC configuration files
- `.gitignore`
- DVC pointer files

The preprocessing script `src/food11/data.py` resizes the Food-11 images to `128x128` and creates the processed and mini processed datasets.

### Is the actual image data on GitHub?

No.

A fresh clone confirmed that Git contains no `.jpg`, `.jpeg`, `.png`, or other image dataset files.

The real dataset directories do not appear immediately after cloning the Git repository.

### Is there a file that points to the data?

Yes.

The repository contains:

- `data_sample.dvc`
- `data/food11_processed.dvc`
- `data/food11_processed_mini.dvc`

These files point DVC to the corresponding stored data.

### Is the data on the DVC/DagsHub remote?

Yes, for the datasets that were intentionally uploaded.

A fresh-clone test successfully restored:

- `data_sample` — 330 files, approximately 19.48 MiB
- `food11_processed` — 16,643 files, approximately 155.02 MiB
- `food11_processed_mini` — 3,292 files, approximately 31.03 MiB

The original raw Food-11 dataset of approximately 1.19 GB was deliberately **not** uploaded.

Therefore:

**GitHub stores the code and DVC pointer files.**

**DagsHub/DVC remote stores the DVC-managed sample and processed datasets.**

---

## Question 7 — Fresh Clone

### Do we see the datasets immediately after cloning?

No.

A fresh clone was created in a separate temporary directory.

Immediately after `git clone`, none of the following directories existed:

- `data_sample/`
- `data/food11_processed/`
- `data/food11_processed_mini/`
- the original raw Food-11 dataset

Git contained only the source/configuration files and DVC pointer files.

No image files were tracked by Git.

### How do we retrieve the data?

The datasets are retrieved using DVC.

Targeted DVC pulls were tested for each pointer file, and the following datasets were restored successfully:

- `data_sample` — 330 files
- `food11_processed` — 16,643 files
- `food11_processed_mini` — 3,292 files

After the pulls, DVC reported:

`Data and pipelines are up to date.`

The full raw dataset was still missing after this test, which was intentional because it was not uploaded.

This demonstrates the separation between Git and DVC:

**`git clone` retrieves code and DVC metadata.**

**`dvc pull` retrieves the actual DVC-managed dataset contents.**

---

## Question 8 — Do you still see `food11_processed` and `food11_processed_mini` after switching to the previous commit?

No.

The repository was switched to the previous data-version commit:

`2b62ed6 — Track sample dataset with DVC`

Then:

```bash
uv run dvc checkout
```

was executed.

At that historical Git commit, only `data_sample.dvc` existed.

Therefore DVC made the working data match that historical state:

- `data_sample/` remained/restored
- `data/food11_processed/` disappeared
- `data/food11_processed_mini/` disappeared

This happened because the processed dataset pointer files did not yet exist in that Git commit.

The repository was then returned to:

```bash
git switch main
uv run dvc checkout
```

The current processed datasets were restored from the DVC cache.

This demonstrates how Git and DVC work together:

- **Git checkout/switch** selects the historical version of the code and `.dvc` pointer files.
- **`dvc checkout`** makes the local datasets match those pointer files.

Therefore, it is possible to reproduce both an older code state and its corresponding data state.

After the exercise, the repository was safely returned to the latest `main` branch.
