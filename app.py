import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from prophet import Prophet

WAQI_TOKEN = "4f30b0c2c6f2ce09551b1ea1935612f97020f23d"  # replace with your real token

# ====== UI Header ======
st.title("🌫️ Air Quality Visualizer")
st.markdown("Welcome to our ISRO Hackathon Project! 🛰️")

# ====== City Selection ======
city = st.selectbox(
    "Choose a city to check AQI:",
    ["Delhi", "Ahmedabad", "Kolkata", "Bengaluru", "Jaipur", "Lucknow", "Pune", "Varanasi", "Hyderabad", "Mumbai", "Custom"]
)

if city == "Custom":
    city = st.text_input("Enter your city name")

# ====== AQI Fetch Button ======
if st.button("🔍 Check AQI") and city:
    st.info(f"Fetching AQI for: {city}")
    try:
        url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
        response = requests.get(url)
        data = response.json()

        if data['status'] == 'ok':
            aqi_data = data['data']
            current_aqi = aqi_data['aqi']
            iaqi = aqi_data['iaqi']
            pm25 = iaqi.get('pm25', {}).get('v', 'N/A')
            pm10 = iaqi.get('pm10', {}).get('v', 'N/A')
            no2 = iaqi.get('no2', {}).get('v', 'N/A')
            so2 = iaqi.get('so2', {}).get('v', 'N/A')
            o3 = iaqi.get('o3', {}).get('v', 'N/A')

            st.success(f"✅ Real-time AQI for {city}: {current_aqi}")

            # --- Pollutant Cards ---
            st.markdown("### 🧪 Pollutant Details")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("PM2.5", pm25)
                st.metric("PM10", pm10)
            with col2:
                st.metric("NO₂", no2)
                st.metric("SO₂", so2)
            with col3:
                st.metric("O₃", o3)
                st.metric("AQI", current_aqi)

            # --- Historical AQI Dummy Data (7 days) ---
            dates = pd.date_range(end=pd.Timestamp.today(), periods=7).to_list()
            aqi_values = np.append(np.random.randint(80, 180, size=6), current_aqi)
            df = pd.DataFrame({'Date': dates, 'AQI': aqi_values})

        else:
            raise Exception(data.get('data', 'Unknown error'))

    except Exception as e:
        current_aqi = np.random.randint(100, 250)
        st.warning(f"⚠️ Failed to fetch live AQI for {city}. Error: {str(e)}. Using dummy value: {current_aqi}")
        dates = pd.date_range(end=pd.Timestamp.today(), periods=7).to_list()
        aqi_values = np.append(np.random.randint(80, 180, size=6), current_aqi)
        df = pd.DataFrame({'Date': dates, 'AQI': aqi_values})

    # ====== AQI Status and Health Advisory ======
    def aqi_status(aqi):
        if aqi <= 50: return "Good 😊", "Air quality is satisfactory.", "success"
        if aqi <= 100: return "Moderate 😐", "Acceptable quality for most.", "info"
        if aqi <= 150: return "Unhealthy for Sensitive 😷", "Sensitive groups may experience effects.", "warning"
        if aqi <= 200: return "Unhealthy 😷", "Everyone may feel effects.", "warning"
        if aqi <= 300: return "Very Unhealthy ☠️", "Health warnings for everyone.", "error"
        return "Hazardous 🚫", "Serious effects. Avoid outdoor activity.", "error"

    status, advice, box = aqi_status(current_aqi)

    # ====== Left Column: Trend | Right Column: Health ======
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 AQI Trend (Past 7 Days)")
        st.line_chart(df.set_index('Date'))
    st.download_button("📥 Download AQI Data (CSV)", df.to_csv(index=False), "aqi_trend.csv")


    with col2:
        st.markdown("### 🩺 Health Recommendation")
        getattr(st, box)(f"Current AQI: **{current_aqi}** → **{status}**\n\n"
                         f"{advice}\n\n"
                         "- Wear a mask if AQI > 150\n"
                         "- Avoid jogging outdoors\n"
                         "- Use air purifiers indoors")

    # ====== Forecasting (Prophet) ======
    st.markdown("### 🔮 AQI Forecast (Next 3 Days)")
    forecast_df = df.rename(columns={'Date': 'ds', 'AQI': 'y'})
    model = Prophet(daily_seasonality=True)
    model.fit(forecast_df)
    future = model.make_future_dataframe(periods=3)
    forecast = model.predict(future)
    forecast_chart = forecast[['ds', 'yhat']].set_index('ds').tail(10)
    st.line_chart(forecast_chart)

    latest_preds = forecast[['ds', 'yhat']].tail(3)
    st.markdown("#### 📆 Predicted AQI Values:")
    for index, row in latest_preds.iterrows():
        st.write(f"{row['ds'].date()} → Predicted AQI: {int(row['yhat'])}")

# ====== Footer ======
st.markdown("---")
st.markdown("""🛰️ Made for ISRO Bhartiya Antariksha Hackathon 2025  
👨‍💻 By Team Bit by Bit""", unsafe_allow_html=True)
