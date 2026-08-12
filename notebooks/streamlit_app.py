import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dự Báo Nhiệt Độ Tokyo", page_icon="🌍", layout="wide")

st.title("🌍 Dashboard Dự Báo Nóng Lên Toàn Cầu (Tokyo)")
st.markdown("Ứng dụng dự báo nhiệt độ trung bình hàng tháng trong tương lai bằng mô hình chuỗi thời gian **Prophet**.")

st.sidebar.header("Thông số đầu vào")
year = st.sidebar.slider("Chọn Năm muốn dự báo", min_value=2024, max_value=2050, value=2030)

if st.sidebar.button("🚀 Dự Báo Ngay"):
    api_url = "http://localhost:8000/predict"
    payload = {"year": year}

    with st.spinner("Đang tính toán dự báo..."):
        try:
            response = requests.post(api_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                avg_temp = result["predicted_avg_temperature"]
                monthly_temps = result["monthly_predictions"]

                st.success("✅ Phân tích hoàn tất!")

                col1, col2 = st.columns(2)
                col1.metric(f"Nhiệt độ Trung bình năm {year}", f"{avg_temp:.2f} °C")

                # Vẽ biểu đồ 12 tháng
                months = [f"Tháng {i}" for i in range(1, 13)]
                df_plot = pd.DataFrame({'Tháng': months, 'Nhiệt độ (°C)': monthly_temps})
                fig = px.line(df_plot, x='Tháng', y='Nhiệt độ (°C)', title=f'Dự báo chi tiết 12 tháng trong năm {year}', markers=True)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Lỗi từ API Backend: Mã lỗi {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Không thể kết nối tới Backend. Hãy chắc chắn rằng bạn đã chạy FastAPI (uvicorn api:app).")
