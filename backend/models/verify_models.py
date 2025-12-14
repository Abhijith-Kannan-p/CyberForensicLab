"""
Utility script to verify that ML models are loaded correctly
"""

import os
import joblib
import numpy as np

def verify_models():
    """Verify that both ML models can be loaded and used"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, 'models')
    
    print("=" * 60)
    print("ML Models Verification")
    print("=" * 60)
    
    # Check XGBoost model
    xgb_path = os.path.join(models_dir, 'attack_classifier_xgb.pkl')
    if os.path.exists(xgb_path):
        print(f"\n✓ Found XGBoost model at: {xgb_path}")
        try:
            xgb_model = joblib.load(xgb_path)
            print(f"  - Model type: {type(xgb_model)}")
            
            # Try to get feature count if available
            if hasattr(xgb_model, 'n_features_in_'):
                print(f"  - Expected features: {xgb_model.n_features_in_}")
            
            # Create dummy features for testing
            n_features = getattr(xgb_model, 'n_features_in_', 41)
            test_features = np.random.rand(1, n_features)
            
            # Test prediction
            prediction = xgb_model.predict(test_features)
            print(f"  - Test prediction: {prediction[0]}")
            
            if hasattr(xgb_model, 'predict_proba'):
                proba = xgb_model.predict_proba(test_features)
                print(f"  - Confidence: {np.max(proba):.4f}")
            
            print("  ✓ XGBoost model loaded successfully!")
            
        except Exception as e:
            print(f"  ✗ Error loading XGBoost model: {str(e)}")
            return False
    else:
        print(f"\n✗ XGBoost model not found at: {xgb_path}")
        return False
    
    # Check Isolation Forest model
    iso_path = os.path.join(models_dir, 'anomaly_detector.pkl')
    if os.path.exists(iso_path):
        print(f"\n✓ Found Isolation Forest model at: {iso_path}")
        try:
            iso_model = joblib.load(iso_path)
            print(f"  - Model type: {type(iso_model)}")
            
            # Try to get feature count if available
            if hasattr(iso_model, 'n_features_in_'):
                print(f"  - Expected features: {iso_model.n_features_in_}")
            
            # Create dummy features for testing
            n_features = getattr(iso_model, 'n_features_in_', 41)
            test_features = np.random.rand(1, n_features)
            
            # Test prediction
            prediction = iso_model.predict(test_features)
            anomaly_score = iso_model.decision_function(test_features)
            print(f"  - Test prediction: {'Anomaly' if prediction[0] == -1 else 'Normal'}")
            print(f"  - Anomaly score: {anomaly_score[0]:.4f}")
            
            print("  ✓ Isolation Forest model loaded successfully!")
            
        except Exception as e:
            print(f"  ✗ Error loading Isolation Forest model: {str(e)}")
            return False
    else:
        print(f"\n✗ Isolation Forest model not found at: {iso_path}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All models verified successfully!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    verify_models()

