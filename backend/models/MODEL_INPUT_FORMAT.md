# Model Input Format Requirements - UNSW-NB15

## Summary

**Both models were trained on UNSW-NB15 dataset** and expect UNSW-NB15 format input.

**Important:** Both models are trained on UNSW-NB15 data, but use different feature subsets:
- **XGBoost**: Uses 3 categorical + numeric features (via preprocessing)
- **Isolation Forest**: Uses only numeric features (proto/service/state are excluded for anomaly detection)

## Dataset Imbalance & Hybrid Approach

**UNSW-NB15 Dataset Characteristics:**
- UNSW-NB15 is extremely imbalanced. Rare classes like Worms have fewer than 50 samples, so the classifier maps them to dominant attack categories.
- To handle this, the system combines **supervised classification** (XGBoost) with **unsupervised anomaly detection** (Isolation Forest), which flags rare behaviors even when classification confidence is low.
- This hybrid approach mirrors real Security Operations Center (SOC) systems, providing both precise attack type classification and comprehensive anomaly detection for rare attack patterns.

**Why This Matters:**
- XGBoost provides accurate classification for common attack types (DoS, Exploits, Reconnaissance, Fuzzers)
- Isolation Forest catches rare or novel attack patterns that may be misclassified by XGBoost
- The combination ensures comprehensive threat detection in production SOC environments

---

## 1. XGBoost Model (attack_classifier_xgb.pkl)

### Expected Input Format
**UNSW-NB15 format** - Raw data with original column names

### Features (33 total):
- **3 Categorical**: `proto` (string), `service` (string), `state` (string)
- **30 Numeric**: See full list below

### How It Works
```
Input (UNSW-NB15) → Preprocessor (ColumnTransformer) → 186 features → XGBoost → Attack Type
```

**Example Input:**
```json
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
  "dload": 0.4,
  "sloss": 0,
  "dloss": 0,
  "sinpkt": 0.1,
  "dinpkt": 0.1,
  "sjit": 0.0,
  "djit": 0.0,
  "swin": 65535,
  "stcpb": 100000,
  "dtcpb": 100000,
  "dwin": 65535,
  "tcprtt": 0.05,
  "synack": 0.01,
  "ackdat": 0.01,
  "smean": 123,
  "dmean": 98,
  "trans_depth": 1,
  "response_body_len": 1000,
  "ct_src_dport_ltm": 5,
  "ct_dst_sport_ltm": 5,
  "is_ftp_login": 0,
  "ct_ftp_cmd": 0,
  "ct_flw_http_mthd": 1,
  "is_sm_ips_ports": 0
}
```

**Key Points:**
- ✅ Column names must match training data **exactly**
- ✅ Preprocessor handles one-hot encoding (proto, service, state) and scaling
- ✅ String values for categorical features are required
- ✅ All 33 features should be included

---

## 2. Isolation Forest Model (anomaly_detector.pkl)

### Expected Input Format
**30 numeric features** extracted from UNSW-NB15 data

### How It Works
```
UNSW-NB15 data → Extract numeric features (proto/service/state excluded) → Isolation Forest → Anomaly Score
```

**Features:**
- All 30 numeric features from UNSW-NB15
- Categorical features (proto, service, state) are **excluded** for anomaly detection
- Total: 30 numeric features only

---

## Full Feature List (UNSW-NB15)

### Categorical Features (3):
1. `proto` - Protocol (tcp, udp, icmp, arp, ospf, sctp)
2. `service` - Application service (http, ftp, smtp, ssh, dns, dhcp, snmp, ssl, -, irc, radius, ftp-data)
3. `state` - Connection state (FIN, CON, INT, REQ, RST, ACC, CLO, URN, no, PAR, ECO, TST, TXD, TXT)

### Numeric Features (30):
1. `dur` - Duration
2. `spkts` - Source packets
3. `dpkts` - Destination packets
4. `sbytes` - Source bytes
5. `dbytes` - Destination bytes
6. `rate` - Rate
7. `sload` - Source load
8. `dload` - Destination load
9. `sloss` - Source loss
10. `dloss` - Destination loss
11. `sinpkt` - Source inter-packet time
12. `dinpkt` - Destination inter-packet time
13. `sjit` - Source jitter
14. `djit` - Destination jitter
15. `swin` - Source window
16. `stcpb` - Source TCP base sequence number
17. `dtcpb` - Destination TCP base sequence number
18. `dwin` - Destination window
19. `tcprtt` - TCP round trip time
20. `synack` - SYN-ACK time
21. `ackdat` - ACK data time
22. `smean` - Source mean
23. `dmean` - Destination mean
24. `trans_depth` - Transaction depth
25. `response_body_len` - Response body length
26. `ct_src_dport_ltm` - Connection count source-destination port
27. `ct_dst_sport_ltm` - Connection count destination-source port
28. `is_ftp_login` - Is FTP login
29. `ct_ftp_cmd` - FTP command count
30. `ct_flw_http_mthd` - HTTP method count
31. `is_sm_ips_ports` - Is same IPs and ports

---

## What We Fixed

### Before (WRONG ❌):
- `test_data.py` was generating NSL-KDD format
- Field names didn't match: `duration` vs `dur`, `protocol_type` vs `proto`, etc.
- Models couldn't process the data correctly

### After (CORRECT ✅):
- `test_data.py` now generates UNSW-NB15 format
- All 33 features included with correct names
- Categorical features use string values
- Backend properly extracts features for both models

---

## Testing

Run the test script:
```bash
python backend/test_data.py
```

This will send UNSW-NB15 format data that matches your training dataset.
