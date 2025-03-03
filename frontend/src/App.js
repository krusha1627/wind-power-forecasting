import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [inputData, setInputData] = useState({
    u10: 2.0,
    v10: -2.0,
    u100: 3.0,
    v100: -3.0,
    hour: 12,
    day: 15,
    month: 6,
    year: 2023,
  });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setInputData({
      ...inputData,
      [name]: parseFloat(value) || 0, 
    });
  };

  const handlePredict = async () => {
    try {
      setLoading(true);
      setError(null);
      
     
      const imgElement = document.getElementById("img");
      const titleElement = document.getElementById("title");
      
      if (imgElement) {
        imgElement.style.height = "100px";
        imgElement.style.width = "200px";
      }
      
      if (titleElement) {
        titleElement.style.fontSize = "25px";
      }
      
      const response = await axios.post('http://127.0.0.1:5000/predict', inputData);
      

      if (response.data.prediction && typeof response.data.prediction === 'object') {

        setPrediction(response.data);
      } else {
 
        setPrediction({
          prediction: {
            normalized_output: response.data.prediction,
            power_output_mw: response.data.prediction * 100, // Assuming 100MW is the maximum
            production_level: getProductionLevel(response.data.prediction)
          },
          input_summary: {
            wind_speed_10m: Math.sqrt(inputData.u10**2 + inputData.v10**2),
            wind_speed_100m: Math.sqrt(inputData.u100**2 + inputData.v100**2)
          }
        });
      }
    } catch (error) {
      console.error('Error making prediction:', error);
      setError(error.response?.data?.error || 'Failed to get prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };


  const getProductionLevel = (normalizedOutput) => {
    if (normalizedOutput < 0.2) return "Low";
    if (normalizedOutput < 0.6) return "Medium";
    return "High";
  };


  const getWindDirection = (u, v) => {
    return ((270 - Math.atan2(v, u) * (180/Math.PI)) % 360).toFixed(1);
  };

  return (
    <div className="App">
      <div className="left-section">
        <img 
          src="https://cdn.pixabay.com/animation/2023/06/29/06/23/06-23-06-393_512.gif" 
          alt="Animated Background" 
          id='img'
        />
      </div>
      
      <div className="content-section">
        <h1 id='title'>Wind Power Production Forecasting</h1>
        
        <div className="input-form">
          <div className="form-section">
            <h3>Wind Parameters</h3>
            <label>
              Zonal Wind Velocity at 10m (u10, m/s):
              <input
                type="number"
                name="u10"
                value={inputData.u10}
                onChange={handleInputChange}
                step="0.1"
              />
            </label>
            <label>
              Meridional Wind Velocity at 10m (v10, m/s):
              <input
                type="number"
                name="v10"
                value={inputData.v10}
                onChange={handleInputChange}
                step="0.1"
              />
            </label>
            <label>
              Zonal Wind Velocity at 100m (u100, m/s):
              <input
                type="number"
                name="u100"
                value={inputData.u100}
                onChange={handleInputChange}
                step="0.1"
              />
            </label>
            <label>
              Meridional Wind Velocity at 100m (v100, m/s):
              <input
                type="number"
                name="v100"
                value={inputData.v100}
                onChange={handleInputChange}
                step="0.1"
              />
            </label>
          </div>
          
          <div className="form-section">
            <h3>Date & Time</h3>
            <label>
              Hour (0-23):
              <input
                type="number"
                name="hour"
                value={inputData.hour}
                onChange={handleInputChange}
                min="0"
                max="23"
              />
            </label>
            <label>
              Day (1-31):
              <input
                type="number"
                name="day"
                value={inputData.day}
                onChange={handleInputChange}
                min="1"
                max="31"
              />
            </label>
            <label>
              Month (1-12):
              <input
                type="number"
                name="month"
                value={inputData.month}
                onChange={handleInputChange}
                min="1"
                max="12"
              />
            </label>
            <label>
              Year (2020-2024):
              <input
                type="number"
                name="year"
                value={inputData.year}
                onChange={handleInputChange}
                min="2020"
                max="2024"
              />
            </label>
          </div>
        </div>
        
        <div className="button-container">
          <button 
            onClick={handlePredict} 
            disabled={loading}
            className={loading ? "loading" : ""}
          >
            {loading ? "Predicting..." : "Predict Wind Power"}
          </button>
        </div>
        
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}
        
        {prediction && (
          <div className="prediction-result">
            <h2>Prediction Results</h2>
            
            <div className="result-card">
              <div className="result-header production-level-{prediction.prediction?.production_level?.toLowerCase() || 'medium'}">
                <h3>Power Production: {prediction.prediction?.production_level || "Medium"}</h3>
              </div>
              
              <div className="result-body">
                <div className="result-item">
                  <span className="result-label">Normalized Output:</span>
                  <span className="result-value">
                    {(prediction.prediction?.normalized_output || 0).toFixed(4)} (0-1 scale)
                  </span>
                </div>
                
                <div className="result-item">
                  <span className="result-label">Estimated Power:</span>
                  <span className="result-value">
                    {(prediction.prediction?.power_output_mw || 0).toFixed(2)} MW
                  </span>
                </div>
                
               
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;