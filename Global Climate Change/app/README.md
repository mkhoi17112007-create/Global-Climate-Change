# 🌍 Climate Change Temperature Forecasting App

Streamlit web application for predicting global temperature using Machine Learning.

## Installation

```bash
pip install -r requirements.txt
```

## Running the App

```bash
streamlit run streamlit_app.py
```

## Features

- **📍 Single Prediction**: Predict temperature for any location and date
- **📊 Batch Forecast**: Generate 12-month forecasts  
- **📈 Model Metrics**: View detailed model performance statistics
- **📉 Interactive Charts**: Visualize predictions with Plotly

## How to Use

1. **Single Prediction Mode:**
   - Select year and month
   - Input latitude and longitude
   - Click "Predict" to get temperature forecast

2. **Batch Forecast Mode:**
   - Enter city name and location coordinates
   - Select year
   - Click "Generate Forecast" for 12-month predictions

3. **Model Info Mode:**
   - View model performance metrics (R², RMSE, MAE)
   - See feature count and training data summary

## Model Information

- **Algorithm**: HistGradientBoosting Regressor
- **Features**: 30+
- **Performance**: 
  - Test R² = 0.97 (Excellent!)
  - Test RMSE = ~0.5°C
  - Test MAE = ~0.4°C
- **Cross-Validation**: R² Mean = 0.97

## Deployment Options

### Streamlit Cloud (Recommended)
1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Sign in with GitHub
4. Click "New app" → Select repo
5. App deploys automatically! 🚀

### Heroku
```bash
# Create app
heroku create <app-name>

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

### Local Development
```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

## Project Structure

```
app/
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── .streamlit/
    └── config.toml          # Streamlit configuration
```

## System Requirements

- Python 3.8+
- 2GB RAM minimum
- Internet connection for model loading

## Troubleshooting

**Issue**: "ModuleNotFoundError: No module named 'streamlit'"
- **Solution**: Run `pip install -r requirements.txt`

**Issue**: Model files not found
- **Solution**: Ensure `model/` folder exists in parent directory with pkl files

**Issue**: Port 8501 already in use
- **Solution**: Run `streamlit run streamlit_app.py --server.port 8502`

## Performance Tips

- Cache model loading with `@st.cache_resource`
- Use batch predictions for multiple locations
- Clear browser cache if UI doesn't update

## Contributing

Feel free to submit issues and improvement suggestions!

## License

This project is part of the Climate Change ML Pipeline course material.

---

**Built with ❤️ using Streamlit | Machine Learning for Climate Science**
