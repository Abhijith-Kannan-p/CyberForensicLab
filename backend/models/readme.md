# Backend API

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place your ML models in the `models/` directory:
   - `attack_classifier_xgb.pkl` - XGBoost attack classifier (with preprocessor and label encoder)
   - `anomaly_detector.pkl` - Isolation Forest anomaly detector

3. Verify models are loaded correctly:
```bash
python verify_models.py
```

4. **Important**: The backend supports **UNSW-NB15 format** data (matching your trained models).
   - **XGBoost**: Receives raw UNSW-NB15 data → Preprocessor transforms to 186 features → Prediction
   - **Isolation Forest**: Receives 30 numeric features extracted from UNSW-NB15 data → Anomaly detection
   - Both models are trained on UNSW-NB15 data, but use different feature subsets:
     - **XGBoost**: Uses 3 categorical + numeric features (via preprocessing)
     - **Isolation Forest**: Uses only numeric features
   - The preprocessor expects the same column names as your training data

5. **Dataset Imbalance Handling**:
   - UNSW-NB15 is extremely imbalanced. Rare classes like Worms have fewer than 50 samples, so the classifier maps them to dominant attack categories.
   - To handle this, the system combines **supervised classification** (XGBoost) with **unsupervised anomaly detection** (Isolation Forest), which flags rare behaviors even when classification confidence is low.
   - This hybrid approach mirrors real Security Operations Center (SOC) systems, providing both precise attack type classification and comprehensive anomaly detection for rare attack patterns.

6. Run the server:
```bash
python app.py
```

## API Endpoints

### `POST /api/submit` - Submit network data for analysis

Submit network traffic data for ML model analysis. The endpoint accepts UNSW-NB15 format data and returns attack classification and anomaly detection results.

**Request Body Example (UNSW-NB15 format):**
```json
{
  "src_ip": "192.168.1.100",
  "dst_ip": "192.168.1.200",
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
}
```

**Important Notes:**
- Field names should match your training data column names **exactly**
- The preprocessor (ColumnTransformer) handles all feature transformation automatically
- String values (like `proto`, `service`, `state`) are supported and will be one-hot encoded
- Include all fields from your training dataset - the preprocessor will use what it needs
- Missing fields will default to 0 or empty string

**Response Example:**
```json
{
  "success": true,
  "node": {
    "id": "node_1",
    "ip": "192.168.1.100",
    "attack_type": "Normal",
    "confidence": 0.95,
    "anomaly_score": 0.1234,
    "is_anomaly": false,
    "timestamp": "2025-12-10T16:00:00",
    "incoming_traffic": 500,
    "outgoing_traffic": 300
  },
  "edge": {
    "source": "192.168.1.100",
    "target": "192.168.1.200",
    "attack_type": "Normal",
    "timestamp": "2025-12-10T16:00:00"
  }
}
```

### Other Endpoints

- `GET /api/nodes` - Get all network nodes
- `GET /api/edges` - Get all network edges
- `GET /api/threats` - Get all detected threats
- `GET /api/stats` - Get dashboard statistics
- `GET /api/health` - Health check endpoint

## WebSocket Events

- `threat_update` - Real-time threat updates sent to all connected clients

## Data Format

Your models were trained on **UNSW-NB15** format data. The backend expects:

### Required Features (33 total):
- **3 Categorical**: `proto` (string), `service` (string), `state` (string)
- **30 Numeric**: `dur`, `spkts`, `dpkts`, `sbytes`, `dbytes`, `rate`, `sload`, `dload`, `sloss`, `dloss`, `sinpkt`, `dinpkt`, `sjit`, `djit`, `swin`, `stcpb`, `dtcpb`, `dwin`, `tcprtt`, `synack`, `ackdat`, `smean`, `dmean`, `trans_depth`, `response_body_len`, `ct_src_dport_ltm`, `ct_dst_sport_ltm`, `is_ftp_login`, `ct_ftp_cmd`, `ct_flw_http_mthd`, `is_sm_ips_ports`

### Processing:
- **XGBoost**: Raw UNSW-NB15 data (all 33 features) → Preprocessor (one-hot encoding + scaling) → 186 features → Prediction
- **Isolation Forest**: 30 numeric features only (proto/service/state are excluded for anomaly detection) → Anomaly detection

The preprocessor expects the same column names as your training dataset exactly.
## Known Limitations

- UNSW-NB15 is highly imbalanced; rare attack classes such as Worms have
  very limited training samples.
- As a result, rare attacks may be mapped to dominant categories during
  classification.
- The anomaly detection model is used to surface such rare or unusual
  behaviors even when classification confidence is low.
