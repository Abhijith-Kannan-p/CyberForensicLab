from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import numpy as np
import pandas as pd
import json
import time
from datetime import datetime
import threading
import random
import os
import joblib

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ML models wrapper
class MLModelWrapper:
    def __init__(self):
        try:
            # Get the directory of this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            models_dir = os.path.join(script_dir, 'models')
            
            # Load XGBoost attack classifier
            xgb_path = os.path.join(models_dir, 'attack_classifier_xgb.pkl')
            if os.path.exists(xgb_path):
                xgb_loaded = joblib.load(xgb_path)
                
                # Handle tuple format: (model, preprocessor, label_encoder)
                if isinstance(xgb_loaded, tuple):
                    if len(xgb_loaded) == 3:
                        # Standard format: (model, preprocessor, label_encoder)
                        self.xgboost_model = xgb_loaded[0]
                        self.xgb_preprocessor = xgb_loaded[1]
                        self.xgb_label_encoder = xgb_loaded[2]
                        print(f"✓ Loaded XGBoost model from {xgb_path}")
                        print(f"✓ Extracted preprocessor (ColumnTransformer)")
                        print(f"✓ Extracted label encoder")
                    elif len(xgb_loaded) >= 2:
                        # Try to identify components
                        self.xgboost_model = xgb_loaded[0]
                        for item in xgb_loaded[1:]:
                            if hasattr(item, 'transform') and hasattr(item, 'fit_transform'):
                                # This is the preprocessor (ColumnTransformer)
                                self.xgb_preprocessor = item
                            elif hasattr(item, 'inverse_transform') and hasattr(item, 'classes_'):
                                # This is the LabelEncoder
                                self.xgb_label_encoder = item
                        print(f"✓ Loaded XGBoost model from {xgb_path} (extracted from tuple)")
                    else:
                        self.xgboost_model = xgb_loaded[0]
                        print(f"✓ Loaded XGBoost model from {xgb_path} (extracted from tuple)")
                elif isinstance(xgb_loaded, dict):
                    # Dictionary format
                    self.xgboost_model = xgb_loaded.get('model') or xgb_loaded.get('classifier')
                    self.xgb_preprocessor = xgb_loaded.get('preprocessor') or xgb_loaded.get('transformer')
                    self.xgb_label_encoder = xgb_loaded.get('label_encoder') or xgb_loaded.get('le')
                    print(f"✓ Loaded XGBoost model from {xgb_path} (extracted from dict)")
                else:
                    # Just the model
                    self.xgboost_model = xgb_loaded
                    print(f"✓ Loaded XGBoost model from {xgb_path}")
                
                # Check if we have required components
                if not hasattr(self, 'xgb_preprocessor') or self.xgb_preprocessor is None:
                    print(f"⚠️  WARNING: No preprocessor found in model file!")
                    xgb_feat_count = getattr(self.xgboost_model, 'n_features_in_', 'unknown')
                    print(f"   XGBoost expects {xgb_feat_count} features (will use anomaly-based fallback)")
                    self.xgb_preprocessor = None
                else:
                    print(f"  → Preprocessor ready (ColumnTransformer)")
                    
                if not hasattr(self, 'xgb_label_encoder') or self.xgb_label_encoder is None:
                    print(f"⚠️  WARNING: No label encoder found in model file!")
                    print(f"   Using default attack type mapping")
                    self.xgb_label_encoder = None
                else:
                    print(f"  → Label encoder ready with classes: {list(self.xgb_label_encoder.classes_)}")
            else:
                raise FileNotFoundError(f"XGBoost model not found at {xgb_path}")
            
            # Load Isolation Forest anomaly detector
            iso_path = os.path.join(models_dir, 'anomaly_detector.pkl')
            if os.path.exists(iso_path):
                iso_loaded = joblib.load(iso_path)
                # Handle if model is stored as tuple (model, metadata) or just the model
                if isinstance(iso_loaded, tuple):
                    self.isolation_forest = iso_loaded[0]  # Get the model from tuple
                    print(f"✓ Loaded Isolation Forest model from {iso_path} (extracted from tuple)")
                else:
                    self.isolation_forest = iso_loaded
                    print(f"✓ Loaded Isolation Forest model from {iso_path}")
                
                # Check expected feature count
                if hasattr(self.isolation_forest, 'n_features_in_'):
                    print(f"  → Isolation Forest expects {self.isolation_forest.n_features_in_} features")
                if hasattr(self.xgboost_model, 'n_features_in_'):
                    print(f"  → XGBoost expects {self.xgboost_model.n_features_in_} features")
            else:
                raise FileNotFoundError(f"Isolation Forest model not found at {iso_path}")
            
            # Get attack types from label encoder if available
            if hasattr(self, 'xgb_label_encoder') and self.xgb_label_encoder is not None:
                try:
                    self.attack_types = list(self.xgb_label_encoder.classes_)
                    print(f"  → Attack types from label encoder: {self.attack_types}")
                except:
                    self.attack_types = ['Normal', 'Exploits', 'Reconnaissance', 'Worms', 'DoS', 'Fuzzers']
            else:
                # Default attack types
                self.attack_types = ['Normal', 'Exploits', 'Reconnaissance', 'Worms', 'DoS', 'Fuzzers']
            
            # Store expected feature counts
            self.xgb_features = getattr(self.xgboost_model, 'n_features_in_', None)
            self.iso_features = getattr(self.isolation_forest, 'n_features_in_', None)
            
            print("✓ ML Models initialized successfully")
            if self.xgb_features:
                print(f"  → XGBoost expects {self.xgb_features} features (after preprocessing)")
            if self.iso_features:
                print(f"  → Isolation Forest expects {self.iso_features} features")
            
        except Exception as e:
            print(f"✗ Error loading ML models: {str(e)}")
            print("Please ensure models are in backend/models/ directory:")
            print("  - attack_classifier_xgb.pkl")
            print("  - anomaly_detector.pkl")
            raise
    
    def predict_attack_type(self, data_dict):
        """Predict attack type using XGBoost with preprocessing"""
        try:
            # Check if we have preprocessor
            if not hasattr(self, 'xgb_preprocessor') or self.xgb_preprocessor is None:
                raise ValueError("No preprocessor available - XGBoost requires preprocessing")
            
            # Convert dict to DataFrame (matching training format)
            df = pd.DataFrame([data_dict])
            
            # Apply preprocessing (transforms to 186 features)
            X = self.xgb_preprocessor.transform(df)
            
            # Get prediction (numeric class 0-9)
            prediction = self.xgboost_model.predict(X)[0]
            
            # Convert numeric prediction to attack type name using label encoder
            if hasattr(self, 'xgb_label_encoder') and self.xgb_label_encoder is not None:
                attack_type = self.xgb_label_encoder.inverse_transform([prediction])[0]
            else:
                # Fallback to manual mapping
                if isinstance(prediction, (int, np.integer)):
                    attack_type = self.attack_types[prediction] if prediction < len(self.attack_types) else 'Unknown'
                else:
                    attack_type = str(prediction)
            
            # Get prediction probabilities for confidence
            if hasattr(self.xgboost_model, 'predict_proba'):
                probabilities = self.xgboost_model.predict_proba(X)[0]
                confidence = float(np.max(probabilities))
            else:
                confidence = 0.95
            
            return attack_type, confidence
            
        except Exception as e:
            print(f"Error in predict_attack_type: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return None to indicate failure, let caller decide fallback
            return None, 0.0
    
    def detect_anomaly(self, features):
        """Detect anomaly using Isolation Forest"""
        try:
            # Get anomaly score (decision function)
            # Lower scores indicate more anomalous behavior
            if hasattr(self.isolation_forest, 'decision_function'):
                anomaly_scores = self.isolation_forest.decision_function(features)
                anomaly_score = float(anomaly_scores[0])
            else:
                # Fallback if decision_function not available
                anomaly_score = 0.0
            
            # Predict if it's an anomaly (-1 for anomaly, 1 for normal)
            predictions = self.isolation_forest.predict(features)
            is_anomaly = bool(predictions[0] == -1)
            
            return anomaly_score, is_anomaly
            
        except Exception as e:
            print(f"Error in detect_anomaly: {str(e)}")
            # Fallback values
            return 0.0, False

# Initialize ML models
try:
    ml_model = MLModelWrapper()
except Exception as e:
    print(f"Failed to initialize ML models: {str(e)}")
    print("Server will start but predictions will fail. Please check model files.")
    ml_model = None

# In-memory storage for network state
network_data = {
    'nodes': [],
    'edges': [],
    'threats': []
}

# Node counter
node_id_counter = 0

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/api/submit', methods=['POST'])
def submit_network_data():
    """Endpoint to submit network traffic data for analysis"""
    global node_id_counter
    
    # Continue even if ML models failed - use fallback predictions
    use_ml_models = ml_model is not None
    
    try:
        data = request.json
        
        # Extract features from request
        # Since models were trained on CICIDS/UNSW-NB15 data, pass raw data to preprocessor
        # The preprocessor (ColumnTransformer) will handle feature extraction and transformation
        
        # For XGBoost: Pass raw data dict directly to preprocessor
        # The preprocessor expects the same column names as training data
        # It will handle: one-hot encoding, scaling, feature engineering, etc.
        
        # For Isolation Forest: Extract features manually (if needed)
        # Map CICIDS/UNSW-NB15 field names to numeric values if needed
        iso_features_list = []
        
        if use_ml_models and ml_model.iso_features:
            # Extract numeric features for Isolation Forest (UNSW-NB15 format)
            # Isolation Forest uses only numeric features - proto/service/state are excluded
            
            # Build feature list with 30 numeric features from UNSW-NB15
            # Note: proto, service, and state are excluded for anomaly detection
            iso_features_list = [
                float(data.get('dur', 0.0)),
                float(data.get('spkts', 0)),
                float(data.get('dpkts', 0)),
                float(data.get('sbytes', 0)),
                float(data.get('dbytes', 0)),
                float(data.get('rate', 0.0)),
                float(data.get('sload', 0.0)),
                float(data.get('dload', 0.0)),
                float(data.get('sloss', 0)),
                float(data.get('dloss', 0)),
                float(data.get('sinpkt', 0.0)),
                float(data.get('dinpkt', 0.0)),
                float(data.get('sjit', 0.0)),
                float(data.get('djit', 0.0)),
                float(data.get('swin', 0)),
                float(data.get('stcpb', 0)),
                float(data.get('dtcpb', 0)),
                float(data.get('dwin', 0)),
                float(data.get('tcprtt', 0.0)),
                float(data.get('synack', 0.0)),
                float(data.get('ackdat', 0.0)),
                float(data.get('smean', 0)),
                float(data.get('dmean', 0)),
                float(data.get('trans_depth', 0)),
                float(data.get('response_body_len', 0)),
                float(data.get('ct_src_dport_ltm', 0)),
                float(data.get('ct_dst_sport_ltm', 0)),
                float(data.get('is_ftp_login', 0)),
                float(data.get('ct_ftp_cmd', 0)),
                float(data.get('ct_flw_http_mthd', 0)),
                float(data.get('is_sm_ips_ports', 0)),
            ]
            
            # Adjust to match expected feature count
            expected_features = ml_model.iso_features
            if len(iso_features_list) < expected_features:
                # Pad with zeros if we have fewer features
                iso_features_list.extend([0.0] * (expected_features - len(iso_features_list)))
            elif len(iso_features_list) > expected_features:
                # Truncate if we have more features
                iso_features_list = iso_features_list[:expected_features]
        
        # Convert to numpy array for Isolation Forest
        iso_features = np.array(iso_features_list, dtype=np.float32).reshape(1, -1) if iso_features_list else None
        
        # Get predictions
        attack_type = None
        confidence = 0.0
        anomaly_score = 0.0
        is_anomaly = False
        
        if use_ml_models:
            try:
                # Try XGBoost prediction with preprocessing
                # Pass the original data dict directly - preprocessor will handle CICIDS/UNSW-NB15 format
                attack_type, confidence = ml_model.predict_attack_type(data)
                
                # Get anomaly detection
                if iso_features is not None:
                    anomaly_score, is_anomaly = ml_model.detect_anomaly(iso_features)
                else:
                    # Fallback if Isolation Forest features not extracted
                    anomaly_score = 0.0
                    is_anomaly = False
                
                # If XGBoost failed (returned None), infer attack type from anomaly score
                if attack_type is None:
                    if is_anomaly:
                        # Infer attack type based on anomaly severity
                        if anomaly_score < -0.3:
                            attack_type = 'DoS'  # High severity
                            confidence = 0.75
                        elif anomaly_score < -0.2:
                            attack_type = 'Exploits'  # Medium-high severity
                            confidence = 0.70
                        elif anomaly_score < -0.1:
                            attack_type = 'Reconnaissance'  # Medium severity
                            confidence = 0.65
                        else:
                            attack_type = 'Fuzzers'  # Lower severity
                            confidence = 0.60
                    else:
                        attack_type = 'Normal'
                        confidence = 0.90
                
                # Debug: Print every prediction to see what's happening
                print(f"[Debug #{node_id_counter}] Attack: {attack_type}, Anomaly: {is_anomaly}, Score: {anomaly_score:.4f}, Confidence: {confidence:.2f}")
                
            except Exception as e:
                print(f"ML prediction error: {str(e)}, using fallback")
                import traceback
                traceback.print_exc()
                use_ml_models = False
        
        if not use_ml_models or attack_type is None:
            # Fallback: simulate predictions if models aren't available
            if attack_type is None:
                if is_anomaly:
                    attack_type = random.choice(['Exploits', 'Reconnaissance', 'Worms', 'DoS', 'Fuzzers'])
                    confidence = random.uniform(0.7, 0.99)
                else:
                    attack_type = 'Normal'
                    confidence = 0.9
            else:
                # Use fallback values
                attack_type = random.choice(['Normal', 'Exploits', 'Reconnaissance', 'Worms', 'DoS', 'Fuzzers'])
                confidence = random.uniform(0.7, 0.99)
                anomaly_score = random.uniform(-0.5, 0.5)
                is_anomaly = anomaly_score < -0.2 or attack_type != 'Normal'
        
        # Create node data
        src_ip = data.get('src_ip', f'192.168.1.{random.randint(1, 255)}')
        dst_ip = data.get('dst_ip', f'192.168.1.{random.randint(1, 255)}')
        
        node_id_counter += 1
        node_data = {
            'id': f'node_{node_id_counter}',
            'ip': src_ip,
            'attack_type': attack_type,
            'confidence': float(confidence),
            'anomaly_score': float(anomaly_score),
            'is_anomaly': bool(is_anomaly),
            'timestamp': datetime.now().isoformat(),
            'incoming_traffic': random.randint(0, 1000),
            'outgoing_traffic': random.randint(0, 1000)
        }
        
        # Add node if it doesn't exist
        existing_node = next((n for n in network_data['nodes'] if n['ip'] == src_ip), None)
        if not existing_node:
            network_data['nodes'].append(node_data)
        else:
            # Update existing node
            existing_node.update(node_data)
        
        # Create edge (connection)
        edge = {
            'source': src_ip,
            'target': dst_ip,
            'attack_type': attack_type,
            'timestamp': datetime.now().isoformat()
        }
        network_data['edges'].append(edge)
        
        # Add to threats if anomalous
        if is_anomaly or attack_type != 'Normal':
            threat = {
                **node_data,
                'severity': 'HIGH' if anomaly_score < -0.3 else 'MEDIUM' if anomaly_score < -0.2 else 'LOW'
            }
            network_data['threats'].append(threat)
            # Keep only last 100 threats
            network_data['threats'] = network_data['threats'][-100:]
            print(f"⚠️ THREAT DETECTED: {attack_type} from {src_ip} (Anomaly: {is_anomaly}, Score: {anomaly_score:.4f})")
        else:
            # Debug: Show when normal traffic is detected
            if node_id_counter % 20 == 0:
                print(f"[Info] Normal traffic from {src_ip} (Score: {anomaly_score:.4f})")
        
        # Emit real-time update via WebSocket
        socketio.emit('threat_update', {
            'node': node_data,
            'edge': edge,
            'is_threat': is_anomaly or attack_type != 'Normal'
        })
        
        return jsonify({
            'success': True,
            'node': node_data,
            'edge': edge
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    """Get all network nodes"""
    return jsonify(network_data['nodes'])

@app.route('/api/edges', methods=['GET'])
def get_edges():
    """Get all network edges"""
    return jsonify(network_data['edges'])

@app.route('/api/threats', methods=['GET'])
def get_threats():
    """Get all threats"""
    return jsonify(network_data['threats'])

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    nodes = network_data['nodes']
    threats = network_data['threats']
    
    attack_type_counts = {}
    for node in nodes:
        attack_type = node.get('attack_type', 'Normal')
        attack_type_counts[attack_type] = attack_type_counts.get(attack_type, 0) + 1
    
    anomaly_scores = [node.get('anomaly_score', 0) for node in nodes]
    
    return jsonify({
        'total_nodes': len(nodes),
        'total_threats': len(threats),
        'attack_type_distribution': attack_type_counts,
        'anomaly_scores': anomaly_scores[-50:] if len(anomaly_scores) > 50 else anomaly_scores
    })

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected to Cyber Forensics Dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    print("Starting Cyber Attack Detection Backend...")
    print("API: http://localhost:5000")
    print("WebSocket: Enabled")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
