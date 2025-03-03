from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
import logging
from logging.handlers import RotatingFileHandler
from flask_cors import CORS
import os
from datetime import datetime
import traceback


MODEL_PATH = 'wind_power_model.pkl'
SCALER_PATH = 'scaler.pkl'
LOG_PATH = 'logs'
MAX_POWER_OUTPUT = 100 


os.makedirs(LOG_PATH, exist_ok=True)


app = Flask(__name__)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


file_handler = RotatingFileHandler(
    os.path.join(LOG_PATH, 'wind_power_api.log'), 
    maxBytes=10485760,  # 10MB
    backupCount=5
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)


try:
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        raise FileNotFoundError(f"Model or scaler file not found at {MODEL_PATH} or {SCALER_PATH}")
    
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    logger.info("Model and scaler loaded successfully.")
except Exception as e:
    logger.critical(f"Error loading model or scaler: {e}")
    logger.critical(traceback.format_exc())
    raise

def validate_input(data):
    """Validate input data for prediction."""
    required_fields = ['u10', 'v10', 'u100', 'v100', 'hour', 'day', 'month', 'year']
    

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    

    try:

        for field in ['u10', 'v10', 'u100', 'v100']:
            if not isinstance(data[field], (int, float)):
                return False, f"Field {field} must be numeric"
        

        if not 0 <= int(data['hour']) <= 23:
            return False, "Hour must be between 0 and 23"
        if not 1 <= int(data['day']) <= 31:
            return False, "Day must be between 1 and 31"
        if not 1 <= int(data['month']) <= 12:
            return False, "Month must be between 1 and 12"
        if not 1900 <= int(data['year']) <= datetime.now().year:
            return False, f"Year must be between 1900 and {datetime.now().year}"
            
    except (ValueError, TypeError) as e:
        return False, f"Invalid data format: {str(e)}"
    
    return True, "Input data is valid"

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint to check if the API is up and running."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'scaler_loaded': scaler is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint to make wind power predictions."""
    try:

        data = request.json
        logger.info(f"Received prediction request with data: {data}")

        is_valid, message = validate_input(data)
        if not is_valid:
            logger.warning(f"Invalid input data: {message}")
            return jsonify({'error': message}), 400
        

        input_data = pd.DataFrame({
            'u10': [float(data['u10'])],
            'v10': [float(data['v10'])],
            'u100': [float(data['u100'])],
            'v100': [float(data['v100'])],
            'hour': [int(data['hour'])],
            'day': [int(data['day'])],
            'month': [int(data['month'])],
            'year': [int(data['year'])],
            'wind_speed_10m': [np.sqrt(float(data['u10'])**2 + float(data['v10'])**2)],
            'wind_speed_100m': [np.sqrt(float(data['u100'])**2 + float(data['v100'])**2)]
        })
        

        wind_direction_10m = (270 - np.degrees(np.arctan2(float(data['v10']), float(data['u10'])))) % 360
        wind_direction_100m = (270 - np.degrees(np.arctan2(float(data['v100']), float(data['u100'])))) % 360
        

        input_scaled = scaler.transform(input_data)
        

        normalized_prediction = float(model.predict(input_scaled)[0])
        

        actual_power = normalized_prediction * MAX_POWER_OUTPUT
        

        if normalized_prediction < 0.2:
            production_level = "Low"
        elif normalized_prediction < 0.6:
            production_level = "Medium"
        else:
            production_level = "High"
            

        logger.info(f"Successful prediction: {normalized_prediction:.4f} (normalized), {actual_power:.2f} MW")
        

        response = {
            'prediction': {
                'normalized_output': round(normalized_prediction, 4),
                'power_output_mw': round(actual_power, 2),
                'production_level': production_level
            },
            'input_summary': {
                'timestamp': f"{data['year']}-{data['month']:02d}-{data['day']:02d} {data['hour']:02d}:00:00",
                'wind_speed_10m': round(float(input_data['wind_speed_10m'].values[0]), 2),
                'wind_direction_10m': round(wind_direction_10m, 2),
                'wind_speed_100m': round(float(input_data['wind_speed_100m'].values[0]), 2),
                'wind_direction_100m': round(wind_direction_100m, 2)
            },
            'meta': {
                'model_version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'request_id': request.headers.get('X-Request-ID', 'not-provided')
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing prediction request: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': "Failed to process prediction request",
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


if __name__ == '__main__':
    logger.info("Starting Wind Power Prediction API")
    app.run(host='0.0.0.0', port=5000, debug=False)