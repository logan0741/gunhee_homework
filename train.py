import os
import sys
import mlflow

sys.path.insert(0, os.path.dirname(__file__))
from app.spam import check_spam

TEST_DATA = [
    ("hello world", "ham"),
    ("how are you doing today", "ham"),
    ("see you tomorrow morning", "ham"),
    ("let's meet for lunch", "ham"),
    ("good morning have a great day", "ham"),
    ("free money win prize now", "spam"),
    ("click here to buy now limited time offer", "spam"),
    ("urgent cash bonus deal discount available", "spam"),
    ("win winner cash prize free offer", "spam"),
    ("free click win bonus discount deal", "spam"),
]


def evaluate(data):
    preds = []
    for text, label in data:
        pred, score = check_spam(text)
        preds.append({"pred": pred, "label": label, "score": score, "correct": pred == label})
    return preds


def compute_metrics(results):
    total = len(results)
    correct = sum(1 for r in results if r["correct"])
    accuracy = correct / total

    spam_actual = [r for r in results if r["label"] == "spam"]
    spam_pred = [r for r in results if r["pred"] == "spam"]
    true_positive = [r for r in spam_pred if r["label"] == "spam"]

    precision = len(true_positive) / len(spam_pred) if spam_pred else 0.0
    recall = len(true_positive) / len(spam_actual) if spam_actual else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}


def main():
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("spamcheck-auto-train")

    spam_keywords = [
        "free", "win", "winner", "prize", "click",
        "buy now", "urgent", "cash", "money", "offer", "deal",
        "discount", "limited time", "bonus"
    ]

    with mlflow.start_run():
        mlflow.log_param("n_keywords", len(spam_keywords))
        mlflow.log_param("threshold", 2)
        mlflow.log_param("n_samples", len(TEST_DATA))

        results = evaluate(TEST_DATA)
        metrics = compute_metrics(results)

        for name, value in metrics.items():
            mlflow.log_metric(name, value)

        mlflow.log_artifact("app/spam.py")

        print(f"[train] tracking_uri={tracking_uri}")
        print(f"[train] accuracy={metrics['accuracy']:.3f}  "
              f"precision={metrics['precision']:.3f}  "
              f"recall={metrics['recall']:.3f}  "
              f"f1={metrics['f1']:.3f}")


if __name__ == "__main__":
    main()
