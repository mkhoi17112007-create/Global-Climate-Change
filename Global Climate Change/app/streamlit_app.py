import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Global Climate Change Forecast",
    page_icon="🌍",
    layout="wide"
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.title("🌍 Global Climate Change")
st.subheader("Monthly Temperature Forecast for Major Countries")
st.caption("Statistical forecast based on historical Berkeley Earth data.")

@st.cache_data(ttl=60)
def get_cities():
    response = requests.get(f"{API_URL}/countries", timeout=30)
    response.raise_for_status()
    return response.json()

@st.cache_data(ttl=60)
def get_model_info():
    response = requests.get(f"{API_URL}/model-info", timeout=30)
    response.raise_for_status()
    return response.json()

cities = get_cities()
info = get_model_info()

with st.sidebar:
    st.header("Filters")
    country = st.selectbox("Country", cities)
    years = st.slider("Forecast horizon (years)", 1, 20, 20)

tab_forecast, tab_single, tab_model = st.tabs([
    "📈 Forecast",
    "🎯 Single Prediction",
    "ℹ️ Model Info"
])

with tab_forecast:
    st.write(f"Historical data ends at **{info['historical_end']}**.")

    if st.button("Generate Forecast", type="primary"):
        response = requests.get(
            f"{API_URL}/forecast",
            params={"country": country, "years": years},
            timeout=120
        )
        response.raise_for_status()

        forecast = pd.DataFrame(response.json())
        forecast["date"] = pd.to_datetime(forecast["date"])

        fig = px.line(
            forecast,
            x="date",
            y="predicted_temperature_c",
            title=f"{city} — {years}-year monthly forecast"
        )
        st.plotly_chart(fig, use_container_width=True)

        annual = (
            forecast.assign(year=forecast["date"].dt.year)
                    .groupby("year", as_index=False)["predicted_temperature_c"]
                    .mean()
        )

        st.subheader("Annual Mean Forecast")
        st.dataframe(annual, use_container_width=True)

        st.metric(
            "Mean forecast temperature",
            f"{forecast['predicted_temperature_c'].mean():.2f} °C"
        )

with tab_single:
    historical_end_year = int(str(info["historical_end"])[:4])

    col1, col2 = st.columns(2)
    with col1:
        year = st.number_input(
            "Year",
            min_value=historical_end_year,
            max_value=historical_end_year + 20,
            value=historical_end_year + 1,
            step=1
        )
    with col2:
        month = st.selectbox("Month", list(range(1, 13)))

    if st.button("Predict selected month"):
        payload = {
            "country": country,
            "year": int(year),
            "month": int(month)
        }
        response = requests.post(
            f"{API_URL}/predict",
            json=payload,
            timeout=60
        )

        if response.ok:
            result = response.json()
            st.metric(
                "Predicted Average Temperature",
                f"{result['predicted_temperature_c']:.2f} °C"
            )
            st.warning(result["warning"])
        else:
            st.error(response.text)

with tab_model:
    st.json(info)
    st.info(
        "The deployment model is selected for long-horizon statistical "
        "extrapolation, not as a physical climate simulator."
    )