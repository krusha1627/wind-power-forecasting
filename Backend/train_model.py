
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data():
    """Load and preprocess the training data."""
    try:
       
        train_df = pd.read_csv('train.csv')
        logging.info("Training data loaded successfully.")
        return train_df
    except Exception as e:
        logging.error(f"Error loading training data: {e}")
        raise

def preprocess_data(train_df):
    """Preprocess the data."""
    try:
        
        train_df['date'] = pd.to_datetime(train_df['date'])

       
        train_df['hour'] = train_df['date'].dt.hour
        train_df['day'] = train_df['date'].dt.day
        train_df['month'] = train_df['date'].dt.month
        train_df['year'] = train_df['date'].dt.year

      
        train_df = train_df.drop(columns=['date'])

      
        train_df['wind_speed_10m'] = np.sqrt(train_df['u10']**2 + train_df['v10']**2)
        train_df['wind_speed_100m'] = np.sqrt(train_df['u100']**2 + train_df['v100']**2)

  
        X = train_df.drop(columns=['production'])
        y = train_df['production']

        logging.info("Data preprocessing completed successfully.")
        return X, y
    except Exception as e:
        logging.error(f"Error preprocessing data: {e}")
        raise

def train_and_save_model(X, y):
    """Train the model and save it to a file."""
    try:
      
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

    
        model = RandomForestRegressor(n_estimators=100, random_state=42)

       
        model.fit(X_scaled, y)
        logging.info("Model trained successfully.")

       
        joblib.dump(model, 'wind_power_model.pkl')
        joblib.dump(scaler, 'scaler.pkl')
        logging.info("Model and scaler saved to disk.")
    except Exception as e:
        logging.error(f"Error training or saving the model: {e}")
        raise

def main():
    """Main function to run the pipeline."""
    try:
       
        train_df = load_data()

        
        X, y = preprocess_data(train_df)

        
        train_and_save_model(X, y)
    except Exception as e:
        logging.error(f"Error in main function: {e}")


if __name__ == "__main__":
    main()