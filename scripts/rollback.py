"""
MLFlow Model Rollback Script

Rolls back the SpamClassifier model in the MLFlow registry to a specific version
by transitioning that version to "Production" and archiving the current one.

Usage:
    # List all versions
    MLFLOW_TRACKING_URI=http://localhost:5000 python scripts/rollback.py --list

    # Rollback to version 1
    MLFLOW_TRACKING_URI=http://localhost:5000 python scripts/rollback.py --version 1
"""
import argparse
import os
import sys
import mlflow
from mlflow.tracking import MlflowClient

MODEL_NAME = "SpamClassifier"


def list_versions(client: MlflowClient):
    versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    if not versions:
        print(f"No versions registered for '{MODEL_NAME}'.")
        return
    print(f"\n{'Version':<10} {'Stage':<15} {'Run ID':<35} {'Created'}")
    print("-" * 80)
    for v in sorted(versions, key=lambda x: int(x.version)):
        print(f"{v.version:<10} {v.current_stage:<15} {v.run_id:<35} {v.creation_timestamp}")


def rollback(client: MlflowClient, target_version: str):
    versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    version_map = {str(v.version): v for v in versions}

    if target_version not in version_map:
        print(f"[rollback] Version {target_version} not found.")
        print(f"[rollback] Available: {sorted([str(v.version) for v in versions])}")
        sys.exit(1)

    for v in versions:
        if v.current_stage == "Production" and str(v.version) != target_version:
            client.transition_model_version_stage(MODEL_NAME, str(v.version), "Archived")
            print(f"[rollback] v{v.version} archived (was Production)")

    client.transition_model_version_stage(MODEL_NAME, target_version, "Production")
    print(f"[rollback] v{target_version} is now PRODUCTION")


def main():
    parser = argparse.ArgumentParser(description="MLFlow model rollback tool")
    parser.add_argument("--list", action="store_true", help="List all model versions")
    parser.add_argument("--version", type=str, help="Target version to rollback to")
    args = parser.parse_args()

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "")
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()

    if args.list:
        list_versions(client)
    elif args.version:
        rollback(client, args.version)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
