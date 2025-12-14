# Data Format Explanation

## The Confusion

**Your models were trained on CICIDS/UNSW-NB15 data**, but the test script has been sending **NSL-KDD/KDD Cup 99 format** data. This is a **mismatch**!

## What Each Model Expects

### 1. XGBoost Model (attack_classifier_xgb.pkl)

**Input Format:** CICIDS/UNSW-NB15 format (raw data with original column names)

**How it works:**
- You send raw CICIDS data: `{"dur": 12.5, "proto": "tcp", "service": "http", ...}`
- The **preprocessor (ColumnTransformer)** transforms it:
  - One-hot encodes categorical features (`proto`, `service`, `state`)
  - Scales numeric features
  - Creates 186 features total
- XGBoost receives the 186 preprocessed features
- Returns attack type prediction

**Required:** The preprocessor expects **exactly the same column names** as your training data.

### 2. Isolation Forest Model (anomaly_detector.pkl)

**Input Format:** 31 numeric features (extracted from CICIDS data)

**How it works:**
- Needs 31 numeric features in a specific order
- These features are extracted from CICIDS data
- Returns anomaly score and anomaly prediction

## What We've Been Sending (WRONG)

The `test_data.py` script has been generating **NSL-KDD format**:
```python
{
  "duration": 12.5,        # Should be "dur"
  "protocol_type": 0,     # Should be "proto": "tcp"
  "service": 15,          # Should be "service": "http" (string)
  "flag": 3,              # Should be "state": "FIN"
  "src_bytes": 1230,      # Should be "sbytes"
  "dst_bytes": 980,       # Should be "dbytes"
  # ... NSL-KDD specific fields
}
```

**This is wrong!** The models expect CICIDS format.

## What We Should Send (CORRECT)

CICIDS/UNSW-NB15 format:
```python
{
  "dur": 12.5,
  "proto": "tcp",
  "service": "http",
  "state": "FIN",
  "spkts": 10,
  "dpkts": 8,
  "sbytes": 1230,
  "dbytes": 980,
  "rate": 12.3,
  "sload": 0.5,
  "dload": 0.4
  # ... all other CICIDS fields
}
```

## The Fix

I need to update `test_data.py` to generate CICIDS format data instead of NSL-KDD format.

**Answer to your question:** 
- ❌ **NO**, you cannot send NSL-KDD format - the models were trained on CICIDS
- ✅ **YES**, you must send CICIDS format - matching your training data
- The preprocessor expects CICIDS column names, not NSL-KDD names

## Next Steps

1. Update `test_data.py` to generate CICIDS format data
2. Ensure all field names match your training dataset exactly
3. Test with actual CICIDS format data

