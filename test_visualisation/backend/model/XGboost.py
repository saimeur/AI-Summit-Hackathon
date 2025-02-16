import joblib
import os
import numpy as np
from xgboost import XGBRegressor

#Create model class
class RiverLevelPredictor:
    def __init__(self):
        self.current_dir = os.path.dirname(__file__)
        self.model = XGBRegressor()
        self.model.load_model(os.path.join(self.current_dir, "xgb_model.json"))
        
        self.scaler_features = joblib.load(os.path.join(self.current_dir, "scaler_features.pkl"))
        self.scaler_target = joblib.load(os.path.join(self.current_dir, "scaler_target.pkl"))

    def create_data_from_curser(self, list_curser):
        return np.title(list_curser, (100, 1))
    
    def preprocess_input(self, X_raw):
        X_scaled = self.scaler_features.transform(X_raw)
        return X_scaled.reshape(1, -1)
    
    def predict(self, X_raw):
        X_preprocessed = self.preprocess_input(X_raw)
        y_pred_scaled = self.model.predict(X_preprocessed)
        y_pred = self.scaler_target.inverse_transform(y_pred_scaled.reshape(-1, 1))
        return y_pred[0][0]