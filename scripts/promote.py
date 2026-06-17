"""
MLFlow Model Promotion Script

Checks the latest experiment run. If accuracy >= ACCURACY_THRESHOLD,
promotes the registered model to Staging (>= 0.85) or Production (>= 0.90).

Usage:
    MLFLOW_TRACKING_URI=http://localhost:5000 python scripts/promote.py
"""
import os
import sys
import mlflow
from mlflow.tracking import MlflowClient

EXPERIMENT_NAME = "spamcheck-ml"
MODEL_NAME = "SpamClassifier"
THRESHOLD_STAGING = float(os.getenv("STAGING_THRESHOLD", "0.85"))
THRESHOLD_PRODUCTION = float(os.getenv("ACCURACY_THRESHOLD", "0.90"))


def main():
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "")
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()

    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        print(f"[promote] Experiment '{EXPERIMENT_NAME}' not found. Run train.py first.")
        sys.exit(1)

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"],
        max_results=1,
    )
    if not runs:
        print("[promote] No runs found.")
        sys.exit(1)

    latest_run = runs[0]
    accuracy = latest_run.data.metrics.get("v2_accuracy", 0.0)
    run_id = latest_run.info.run_id
    print(f"[promote] Latest run {run_id} | v2_accuracy={accuracy:.4f}")

    try:
        versions = client.search_model_versions(f"name='{MODEL_NAME}'")
        if not versions:
            print(f"[promote] No registered versions for '{MODEL_NAME}'. Skipping.")
            return

        latest_version = sorted(versions, key=lambda v: int(v.version))[-1]
        version_num = latest_version.version

        if accuracy >= THRESHOLD_PRODUCTION:
            client.transition_model_version_stage(MODEL_NAME, version_num, "Production")
            print(f"[promote] v{version_num} promoted to PRODUCTION (accuracy={accuracy:.4f})")
        elif accuracy >= THRESHOLD_STAGING:
            client.transition_model_version_stage(MODEL_NAME, version_num, "Staging")
            print(f"[promote] v{version_num} promoted to STAGING (accuracy={accuracy:.4f})")
        else:
            print(f"[promote] accuracy={accuracy:.4f} below threshold={THRESHOLD_STAGING}. Not promoted.")
    except Exception as e:
        print(f"[promote] Model Registry error: {e}")


if __name__ == "__main__":
    main()
