# 3D Cyber Attack Detection and Visualization System

An immersive 3D network visualization dashboard that uses machine learning (XGBoost + Isolation Forest) to classify network attacks and detect anomalies in real-time, visualized through a Three.js-powered 3D network graph.

## Features

### 🎯 3D Network Visualization
- **Interactive 3D Network Graph**: Each node represents a device/server/system
- **Animated Edges**: Network communication visualized as animated neon lines
- **Dynamic Node Styling**: 
  - Node color indicates attack type
  - Glow intensity shows anomaly severity
  - Pulsing animation indicates live threats
- **Camera Controls**: Pan, rotate, zoom, and orbit around the network
- **Auto-focus**: Camera automatically focuses on suspicious nodes

### 🎨 Real-Time Threat Visualization
- **Attack Type Colors**:
  - 🔵 Normal: Blue
  - 🟣 Exploits: Purple
  - 🟢 Reconnaissance: Green
  - 🔴 Worms: Red
  - 🟠 DoS: Orange
  - 🟡 Fuzzers: Yellow
- **Anomaly Detection**: Nodes glow and pulse based on anomaly scores
- **Attack Flows**: Animated neon arcs traveling between nodes

### 📊 Dashboard & Analytics
- **Attack Type Distribution**: Pie chart showing attack type breakdown
- **Live Anomaly Graph**: Real-time anomaly score visualization
- **Threat Log Table**: Sortable table with search functionality
- **Node Details Panel**: Click any node to see detailed attack information

### 🔧 Technical Stack
- **Frontend**: React + Vite + Three.js + Tailwind CSS
- **Backend**: Python Flask + Flask-SocketIO
- **ML Models**: XGBoost (classification) + Isolation Forest (anomaly detection)
- **Real-time**: WebSocket for live updates

### 📊 Dataset & Model Architecture

**UNSW-NB15 Dataset Characteristics:**
- UNSW-NB15 is extremely imbalanced. Rare classes like Worms have fewer than 50 samples, so the classifier maps them to dominant attack categories.
- To handle this, the system combines **supervised classification** (XGBoost) with **unsupervised anomaly detection** (Isolation Forest), which flags rare behaviors even when classification confidence is low.
- This hybrid approach mirrors real Security Operations Center (SOC) systems, providing both precise attack type classification and comprehensive anomaly detection for rare attack patterns.

## Installation

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Add your ML models:
   - Place your XGBoost model at `backend/models/attack_classifier_xgb.pkl`
   - Place your Isolation Forest model at `backend/models/anomaly_detector.pkl`
   - Update `backend/app.py` to load your models (see comments in code)

4. Start the backend server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Usage

### Submitting Network Data

Send POST requests to `http://localhost:5000/api/submit` with network traffic data:

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
  "dload": 0.4,
  "smean": 123,
  "dmean": 98
}

```

### Testing with Sample Data

A test script is provided to generate sample network data:

```bash
python backend/test_data.py
```

## API Endpoints

- `POST /api/submit` - Submit network data for analysis
- `GET /api/nodes` - Get all network nodes
- `GET /api/edges` - Get all network edges
- `GET /api/threats` - Get all detected threats
- `GET /api/stats` - Get dashboard statistics

## WebSocket Events

- `threat_update` - Real-time threat updates sent to all connected clients

## Project Structure

```
CyberForensics/
├── backend/
│   ├── app.py              # Flask backend with ML integration
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Backend documentation
├── src/
│   ├── components/
│   │   ├── Network3D.jsx  # 3D network visualization
│   │   ├── SidePanel.jsx  # Node details panel
│   │   └── Dashboard.jsx  # Analytics dashboard
│   ├── App.jsx            # Main React component
│   ├── main.jsx           # React entry point
│   └── index.css          # Global styles
├── package.json           # Frontend dependencies
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
└── README.md              # This file
```

## Customization

### Adding Your ML Models

1. Save your trained models:
   - XGBoost classifier: `backend/models/attack_classifier_xgb.pkl`
   - Isolation Forest: `backend/models/anomaly_detector.pkl`

2. Update `backend/app.py`:
```python
import joblib

class MLModelWrapper:
    def __init__(self):
        self.attack_classifier_xgb = joblib.load('models/attack_classifier_xgb.pkl')
        self.isolation_forest = joblib.load('models/anomaly_detector.pkl')
```

### Customizing Attack Types

Update the `attack_types` list in `backend/app.py` and the color mappings in `src/components/Network3D.jsx` and `src/components/Dashboard.jsx`.

## ML Model Architecture

### Hybrid Detection Approach

The system uses a two-stage detection pipeline:

1. **Supervised Classification (XGBoost)**: Classifies network traffic into major known attack categories
(Normal, DoS, Exploits, Fuzzers, Reconnaissance). Rare attacks
(e.g., Worms) are primarily surfaced via anomaly detection due to
extreme class imbalance in UNSW-NB15.

2. **Unsupervised Anomaly Detection (Isolation Forest)**: Detects rare or novel attack patterns that may not be well-represented in the training data

**Why Both Models?**
- UNSW-NB15 is extremely imbalanced. Rare classes like Worms have fewer than 50 samples, so the classifier maps them to dominant attack categories.
- To handle this, the system combines supervised classification with unsupervised anomaly detection, which flags rare behaviors even when classification confidence is low.
- This hybrid approach mirrors real Security Operations Center (SOC) systems, providing both precise attack type classification and comprehensive anomaly detection for rare attack patterns.

## Performance Notes

- The 3D scene renders up to 100 edges at a time for performance
- Threat log displays the most recent 10 threats
- Anomaly scores graph shows the last 50 data points

## License

MIT License - feel free to use this project for your cybersecurity needs!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

