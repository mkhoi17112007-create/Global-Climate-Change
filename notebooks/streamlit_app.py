import streamlit as st
import requests

st.set_page_config(page_title="Dự Báo Nhiệt Độ", page_icon="🌍", layout="wide")

st.title("🌍 Dashboard Dự Báo Nhiệt Độ Bề Mặt Trái Đất")
st.markdown("Ứng dụng dự báo nhiệt độ trung bình hàng tháng dựa trên dữ liệu lịch sử và mô hình Machine Learning.")

# Form nhập liệu ở Sidebar
st.sidebar.header("Thông số đầu vào")
year = st.sidebar.number_input("Năm (Year)", min_value=2000, max_value=2100, value=2026)
month = st.sidebar.slider("Tháng (Month)", 1, 12, 8)
lag_1 = st.sidebar.number_input("Nhiệt độ tháng trước (Lag 1) °C", value=25.0)
lag_12 = st.sidebar.number_input("Nhiệt độ cùng kỳ năm ngoái (Lag 12) °C", value=24.5)
rolling_mean_12 = st.sidebar.number_input("Nhiệt độ trung bình 12 tháng (Rolling Mean) °C", value=24.8)

if st.sidebar.button("🚀 Dự Báo Ngay"):
    # URL của FastAPI Backend
    api_url = "http://localhost:8000/predict"
    payload = {
        "year": year,
        "month": month,
        "lag_1": lag_1,
        "lag_12": lag_12,
        "rolling_mean_12": rolling_mean_12
    }

    with st.spinner("Đang tính toán dự báo..."):
        try:
            response = requests.post(api_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                pred_temp = result["predicted_temperature"]
                st.success("✅ Hoàn tất!")

                # Hiển thị Dashboard trực quan (KPI)
                col1, col2, col3 = st.columns(3)
                col1.metric("Nhiệt độ tháng trước", f"{lag_1:.2f} °C")
                col2.metric("Nhiệt độ dự báo", f"{pred_temp:.2f} °C", f"{pred_temp - lag_1:.2f} °C so với tháng trước")
                col3.metric("Nhiệt độ TB 12 tháng", f"{rolling_mean_12:.2f} °C")

            else:
                st.error(f"Lỗi từ API Backend: Mã lỗi {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Không thể kết nối tới Backend. Hãy chắc chắn rằng bạn đã chạy FastAPI (uvicorn api:app).")
