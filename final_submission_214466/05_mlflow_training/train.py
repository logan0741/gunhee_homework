import os
import sys
import pickle

import mlflow
import mlflow.sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.dirname(__file__))
from data.dataset import DATASET

_SPAM_KEYWORDS = [
    "free", "win", "winner", "prize", "click",
    "buy now", "urgent", "cash", "money", "offer", "deal",
    "discount", "limited time", "bonus",
]


def _keyword_predict(texts):
    results = []
    for text in texts:
        t = text.lower()
        hits = sum(1 for kw in _SPAM_KEYWORDS if kw in t)
        results.append(1 if hits >= 2 else 0)
    return results


def compute_metrics(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
    }


def main():
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "")
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("spamcheck-ml")

    texts = [item[0] for item in DATASET]
    labels = [item[1] for item in DATASET]

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    max_features = int(os.getenv("MAX_FEATURES", "1000"))
    ngram_max = int(os.getenv("NGRAM_MAX", "2"))
    alpha = float(os.getenv("NB_ALPHA", "1.0"))

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, ngram_max),
            stop_words="english",
        )),
        ("clf", MultinomialNB(alpha=alpha)),
    ])

    with mlflow.start_run() as run:
        mlflow.log_params({
            "model_type": "TF-IDF + MultinomialNB",
            "max_features": max_features,
            "ngram_range": f"(1,{ngram_max})",
            "nb_alpha": alpha,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        })

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        v2_metrics = compute_metrics(y_test, y_pred)
        for k, v in v2_metrics.items():
            mlflow.log_metric(f"v2_{k}", v)

        v1_pred = _keyword_predict(X_test)
        v1_metrics = compute_metrics(y_test, v1_pred)
        for k, v in v1_metrics.items():
            mlflow.log_metric(f"v1_{k}", v)

        try:
            mlflow.sklearn.log_model(
                pipeline,
                artifact_path="spam_pipeline",
                registered_model_name="SpamClassifier",
            )
        except Exception as e:
            print(f"[train] Model Registry not available: {e}")
            mlflow.sklearn.log_model(pipeline, artifact_path="spam_pipeline")

        os.makedirs("models", exist_ok=True)
        model_path = "models/spam_pipeline.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(pipeline, f)
        mlflow.log_artifact(model_path)

        print(f"[train] Run ID: {run.info.run_id}")
        print(f"[train] V1 (keyword) accuracy={v1_metrics['accuracy']:.4f}  "
              f"f1={v1_metrics['f1']:.4f}")
        print(f"[train] V2 (ML)      accuracy={v2_metrics['accuracy']:.4f}  "
              f"f1={v2_metrics['f1']:.4f}")

    return v2_metrics


if __name__ == "__main__":
    main()
