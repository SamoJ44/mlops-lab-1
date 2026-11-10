# Lab 5 - CI/CD with GitHub Actions

## Question 1
Loading the real model in unit tests is not a good idea because the tests depend on the MLflow server. If the server is down or the connection fails the test will fail even if our code is correct. Also loading the model takes time and makes tests slower.

## Question 2
The test proves that the API can receive an image, process it and return JSON with a category and confidence. But it doesnt prove that the real model is accurate or that it correctly classifies real images because we used a fake model with a fixed output.

## Question 3
The cross-split duplicate check detected the problem by comparing MD5 hashes. In our original mini dataset it found 43 duplicate files across the splits. We removed them in a separate cleaned copy and all five validation checks passed.

A duplicate between training and testing is more dangerous because the model might have already seen the image during training so its test accuracy can look better than it really is. A corrupted image usually causes an obvious error but a duplicate can go unnoticed.

## Question 4
We can run `validate_data.py` locally after pulling the data with DVC and before pushing or training. We can also run it in an automated training pipeline on a machine that has access to the DVC data before training starts.

## Question 5
If a unit test fails the `smoke` job will be skipped because it has `needs: test`. Without this dependency the two jobs could run independently so the smoke job might run even when the unit tests fail.

## Question 6
The first GitHub Actions run took **[fill in first run time]** and the second run took **[fill in second run time]**.

The `uv sync` step should be faster on the second run if the dependency cache was reused so it doesnt have to download all packages again. We need to compare the actual run logs to confirm which step improved.

## Question 7
We tag the Docker image with the commit SHA because it identifies exactly which version of the code was used. If two machines pull `latest` at different times and a new image gets pushed between them they can end up running different code even though both pulled `latest`. Using the SHA also makes it easier to reproduce or roll back a release.

## Question 8
We set `permissions` explicitly to give the GitHub token only what the job needs. The image publishing job needs `contents: read` and `packages: write`. If a compromised step had too many permissions it could modify repository files or workflows, publish unwanted packages or access information that the token is allowed to read.

## Question 9
**[Complete after testing branch protection with a pull request.]**

When we push a branch with a broken test the pull request should show a failed check with a red X. With the required `test` and `smoke` checks and pull request protection enabled the merge should be blocked until the checks pass. This is better for a team because the checks run the same way for everybody instead of depending on each person testing locally.

## Question 10
**[Complete after implementing and running `promote.py` on two model versions.]**

- Current champion accuracy: **[fill in]**
- Candidate 1 version and accuracy: **[fill in]**
- Candidate 1 gate decision: **[champion or challenger]**
- Candidate 2 version and accuracy: **[fill in]**
- Candidate 2 gate decision: **[champion or challenger]**
- Test split size `n`: **[fill in]**
- `2 * se` in accuracy points: **[fill in]**

We calculate `se = sqrt(p * (1 - p) / n)` where `p` is the current champion test accuracy and `n` is the number of test images. The candidate only becomes champion if its accuracy is at least the old champion accuracy plus `2 * se`. Otherwise it becomes challenger.

## Question 11
One way is to run the promotion script automatically at the end of training on our local machine where MLflow is available. Another way is to use a hosted MLflow server like DagsHub so a GitHub Actions workflow can connect to it and run the script after training.

## Question 12
Our pipeline starts with a git push. GitHub Actions automatically checks the code using Ruff and unit tests. If those pass it builds the Docker image and runs a container with `SKIP_MODEL=1` to check `/health`. On `main` it then pushes the image to GitHub Container Registry tagged with the commit SHA.

The code version is decided by the Git commit SHA. The model version is separate and is selected through the `champion` alias in MLflow. Training, model promotion and deploying the new image are not yet part of the automatic GitHub workflow.

```text
Git push -> GitHub Actions (automatic) -> Ruff lint + unit tests (automatic) --> Docker build (automatic)
-->Smoke test /health (automatic) --> Push image to GHCR on main (automatic) --> Code version = commit SHA --> Deploy image (manual for now) --> Running FastAPI container --> Load MLflow model: food11@champion
   Model version = MLflow alias

Separate model path:
Training (manual/current setup)
   |
   v
Register candidate in MLflow
   |
   v
Run promotion quality gate (manual/current setup)
   |
   +--> Promoted: move champion alias
   |
   +--> Not promoted: set challenger alias
```
