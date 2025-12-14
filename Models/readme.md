# Machine Learning Models

This directory contains the trained machine learning models used by the backend
for real-time cyber attack detection and anomaly analysis.

## Models

- **attack_classifier_xgb.pkl**  
  XGBoost-based multi-class attack classifier trained on the UNSW-NB15 dataset.
  This model predicts the attack category for incoming network traffic.

- **anomaly_detector.pkl**  
  Isolation Forest model used for unsupervised anomaly detection. It identifies
  rare or abnormal network behavior that may indicate novel or low-frequency attacks.

## Usage

The backend automatically loads these models at startup. Ensure both files are
present in this directory before running the server:

```bash
python app.py
