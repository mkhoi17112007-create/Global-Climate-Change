import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="🌍 Climate Change Temperature Forecasting",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .header-text {
        color: #1f77b4;
        font-size: 2.5em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Load model and artifacts
@st.cache_resource
def load_model_artifacts():
    model_dir = 'model/'
    metrics = joblib.load(os.path.join(model_dir, 'metrics.pkl'))
    best_model_name = metrics['best_model_name'].replace(" ", "_").lower()
    best_model = joblib.load(os.path.join(model_dir, f"{best_model_name}.pkl"))
    scaler = joblib.load(os.path.join(model_dir, 'scaler.pkl'))
    feature_names = joblib.load(os.path.join(model_dir, 'feature_names.pkl'))
    return best_model, scaler, feature_names, metrics

best_model, scaler, feature_names, metrics = load_model_artifacts()

def prepare_features(data_dict):
    X = pd.DataFrame([data_dict])
    for feat in feature_names:
        if feat not in X.columns:
            X[feat] = 0
    X = X[feature_names]
    numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns
    X_scaled = X.copy()
    X_scaled[numeric_cols] = scaler.transform(X[numeric_cols])
    return X_scaled

def predict_temperature(data_dict):
    X_prepared = prepare_features(data_dict)
    predicted_temp = best_model.predict(X_prepared)[0]
    return predicted_temp

# Title
st.markdown('<p class="header-text">🌍 Climate Change Temperature Forecasting</p>', 
            unsafe_allow_html=True)

st.markdown("""Climate Change Temperature Prediction using Machine Learning.
Predict future temperatures for any location on Earth based on historical data.""")

# Sidebar
st.sidebar.title("⚙️ Settings")
app_mode = st.sidebar.radio("Choose Mode:", 
    ["📍 Single Prediction", "📊 Batch Forecast", "📈 Model Info"])

if app_mode == "📍 Single Prediction":
    st.header("📍 Single Location Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        year = st.slider("Year:", 2020, 2050, 2025)
        month = st.selectbox("Month:", range(1, 13), format_func=lambda x: 
            ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][x-1])
    
    with col2:
        latitude = st.slider("Latitude:", -90.0, 90.0, 10.82, step=0.01)
        longitude = st.slider("Longitude:", -180.0, 180.0, 106.63, step=0.01)
    
    if st.button("🔮 Predict"):
        data = {
            'Year': year, 'Month': month,
            'Quarter': (month - 1) // 3 + 1,
            'DayOfYear': month * 30,
            'Week': month * 4,
            'Season_Encoded': (month - 1) // 3,
            'Lat': latitude, 'Lon': longitude,
            'Lat_norm': latitude / 90,
            'Lon_norm': longitude / 180,
            'Hemisphere_Encoded': (1 if latitude >= 0 else 0) * 2 + (1 if longitude >= 0 else 0),
            'city_temp': 20, 'country_temp': 20
        }
        
        pred = predict_temperature(data)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Predicted Temperature", f"{pred:.2f}°C")
        with col2:
            st.metric("Location", f"({latitude:.2f}°, {longitude:.2f}°)")
        with col3:
            st.metric("Date", f"{year}-{month:02d}")

elif app_mode == "📊 Batch Forecast":
    st.header("📊 Yearly Forecast (12 Months)")
    
    col1, col2 = st.columns(2)
    with col1:
        year = st.slider("Year:", 2020, 2050, 2025)
    with col2:
        city_name = st.text_input("City Name:", "Ho Chi Minh City")
    
    latitude = st.slider("Latitude:", -90.0, 90.0, 10.82)
    longitude = st.slider("Longitude:", -180.0, 180.0, 106.63)
    
    if st.button("📈 Generate Forecast"):
        predictions = []
        months_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for month in range(1, 13):
            data = {
                'Year': year, 'Month': month,
                'Quarter': (month - 1) // 3 + 1,
                'DayOfYear': month * 30,
                'Week': month * 4,
                'Season_Encoded': (month - 1) // 3,
                'Lat': latitude, 'Lon': longitude,
                'Lat_norm': latitude / 90,
                'Lon_norm': longitude / 180,
                'Hemisphere_Encoded': (1 if latitude >= 0 else 0) * 2 + (1 if longitude >= 0 else 0),
                'city_temp': 20, 'country_temp': 20
            }
            pred = predict_temperature(data)
            predictions.append(pred)
        
        df_forecast = pd.DataFrame({
            'Month': months_names,
            'Temperature (°C)': predictions
        })
        
        # Chart
        fig = px.line(df_forecast, x='Month', y='Temperature (°C)',
                     markers=True, title=f"Temperature Forecast - {city_name} ({year})")
        fig.update_layout(hovermode='x unified', height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Table
        st.dataframe(df_forecast, use_container_width=True)
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average", f"{np.mean(predictions):.2f}°C")
        with col2:
            st.metric("Highest", f"{np.max(predictions):.2f}°C")
        with col3:
            st.metric("Lowest", f"{np.min(predictions):.2f}°C")

elif app_mode == "📈 Model Info":
    st.header("📈 Model Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Test R²", f"{metrics['test_r2']:.4f}")
    with col2:
        st.metric("Test RMSE", f"{metrics['test_rmse']:.4f}°C")
    with col3:
        st.metric("Test MAE", f"{metrics['test_mae']:.4f}°C")
    with col4:
        st.metric("CV R² Mean", f"{metrics['cv_r2_mean']:.4f}")
    
    st.info(f"""**Model Summary:**
- Model: {metrics['best_model_name']}
- Features: {metrics['n_features']}
- Training samples: {metrics['n_train_samples']:,}
- Test samples: {metrics['n_test_samples']:,}
- Cross-validation R² (mean): {metrics['cv_r2_mean']:.4f}
    """)

st.sidebar.markdown("---")
st.sidebar.info("🌍 Climate Change ML Project | Built with Streamlit")
