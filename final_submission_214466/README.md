# Final Submission - SpamCheck

This folder contains the final project package organized in pipeline order.

## Folder Order

```text
01_service_app/
02_tests/
03_docker/
04_github_actions/
05_mlflow_training/
06_model_ops/
07_model_artifacts/
08_evidence_screenshots/
09_report/
```

## 01_service_app

Contains the FastAPI service code.

- `app/main.py`: API routes, logging, model info, model reload
- `app/spam.py`: model loading and spam prediction
- `app/issue.py`: optional GitHub Issue creation on errors
- `static/index.html`: simple web UI

## 02_tests

Contains pytest tests.

- API contract test
- spam/ham prediction tests
- model version check

Run from the project root:

```powershell
python -m pytest -q
```

## 03_docker

Contains deployment and runtime files.

- `Dockerfile`
- `compose.yaml`
- `.dockerignore`
- `requirements.txt`

Build and run:

```powershell
docker build -t spamcheck:local .
docker run --rm -p 10000:10000 -e PORT=10000 spamcheck:local
```

## 04_github_actions

Contains GitHub Actions workflows.

- `ci.yml`: run tests
- `docker-verify.yml`: verify Docker build and HTTP response
- `mlflow-train.yml`: run model training and MLflow logging
- `auto-promote.yml`: promote model by metric threshold

## 05_mlflow_training

Contains the training pipeline.

- `train.py`: trains TF-IDF + MultinomialNB model
- `data/dataset.py`: labeled spam/ham dataset

Training output:

```text
models/spam_pipeline.pkl
```

## 06_model_ops

Contains model operation helpers.

- `scripts/promote.py`: promote a registered model version
- `scripts/rollback.py`: roll back to an older model version
- `mlflow-server/Dockerfile`: MLflow server container definition

## 07_model_artifacts

Contains the trained model artifact used by the service.

- `models/spam_pipeline.pkl`

## 08_evidence_screenshots

Contains screenshots used as project evidence.

- FastAPI UI
- Swagger docs
- model info API
- MLflow experiment and model screens
- GitHub Actions screen
- Git log screen

## 09_report

Contains the final project report PDF.

```text
기말프로젝트_보고서_214466_김건희.pdf
```

## Local Run Check

From the project root:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 10000
```

Open:

```text
http://127.0.0.1:10000/
http://127.0.0.1:10000/docs
```

Expected model info:

```json
{"model_version":"ml-v2"}
```
