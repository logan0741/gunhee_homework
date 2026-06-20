# SpamCheck

SpamCheck is a FastAPI web service that classifies short text as spam or ham. The service uses a scikit-learn model when `models/spam_pipeline.pkl` is available and falls back to a keyword-based classifier if the model file is missing.

## Features

- Web UI for entering text and checking the classification result
- `POST /classify` API returning `label` and `score`
- `GET /model/info` API for checking the active model mode
- `POST /model/reload` API for reloading the model file without restarting the app
- pytest tests for the API contract and spam classification logic
- Dockerfile and GitHub Actions workflows for test, Docker verification, and MLflow training

## Project Structure

```text
app/
  main.py      FastAPI routes and logging
  spam.py      model loading and prediction logic
data/
  dataset.py   labeled spam/ham training data
scripts/
  promote.py   MLflow model promotion helper
  rollback.py  MLflow model rollback helper
tests/
  test_api.py
  test_spam.py
train.py       model training and MLflow logging
```

## Run Locally

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 10000
```

Open:

```text
http://127.0.0.1:10000/
http://127.0.0.1:10000/docs
```

## Test

```powershell
python -m pytest -q
```

## Train Model

```powershell
python train.py
```

The training script logs parameters and metrics to MLflow and writes the trained pipeline to:

```text
models/spam_pipeline.pkl
```

## Docker

```powershell
docker build -t spamcheck:local .
docker run --rm -p 10000:10000 -e PORT=10000 spamcheck:local
```

## API Example

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:10000/classify `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"text":"You have won a free prize click here now"}'
```

Example response:

```json
{
  "label": "spam",
  "score": 0.7811
}
```

## Notes

Local report files, generated PDFs, generated HTML files, MLflow runs, and cache files are excluded from Git. Only source code, tests, workflows, the trained model file, and this README are intended to be tracked.

## Final Submission Folder

The `final_submission_214466/` folder contains the project files arranged in pipeline order and includes the final report PDF.
