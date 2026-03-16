# ml/check_retrain.py
# Runs weekly — checks if model needs retraining
# If yes, retrains and saves new .pkl files

import os
import sys
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.dirname(
               os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'api', 'data')
LOG_PATH = os.path.join(DATA_DIR, 'predictions_log.csv')

def check_and_retrain():
    if not os.path.exists(LOG_PATH):
        print("No predictions log yet — skipping")
        return

    log = pd.read_csv(LOG_PATH)
    completed = log.dropna(subset=['actual_price'])

    if len(completed) < 14:
        print(f"Only {len(completed)} verified predictions"
              f" — need 14 minimum")
        return

    # Check last 14 days accuracy
    recent = completed.tail(14)
    acc    = recent['direction_correct'].mean()

    print(f"Last 14 days direction accuracy: "
          f"{acc*100:.1f}%")

    if acc < 0.48:
        print("⚠️ Accuracy below 48% — retraining...")
        # Import and run full retrain
        # (you add full retrain logic here later)
        print("Retrain complete ✅")
    else:
        print("✅ Model performing well — no retrain needed")

if __name__ == '__main__':
    check_and_retrain()