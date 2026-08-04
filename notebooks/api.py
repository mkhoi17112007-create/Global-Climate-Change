from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import uvicorn

# == 1. KHỞI TẠO FASTAPI ===
app = FastAPI(
    title="Climate Change Temperature Prediction API",
    description="API dự đoán nhiệt độ trung bình hàng tháng dựa trên mô hình XGBoost.",
    version="1.0"
)

# == 2. LOAD MODEL ===
# Giả sử bạn đã lưu mô hình tốt nhất từ Notebook 06 vào thư mục models/ (hoặc từ Model.py vào thư mục model/)
try:
    # Load file pkl mô hình ở đây
    model = joblib.load("../model/xgboost_model.pkl") 
    print("Đã load mô hình XGBoost thành công")
except Exception as e:
    print("Cảnh báo load model:", e)
    model = None

# == 3. MÔ TẢ CẤU TRÚC DỮ LIỆU ===
class PredictionInput(BaseModel):
    year: int
    month: int
    lag_1: float
    lag_12: float
    rolling_mean_12: float

# == 4. CÁC ENDPOINT API ===
@app.post("/predict")
def predict_temperature(data: PredictionInput):
    if model is None:
        raise HTTPException(status_code=500, detail="Model chưa được nạp. Hãy huấn luyện và lưu file mô hình trước.")

    input_df = pd.DataFrame([data.dict()])

    try:
        pred = model.predict(input_df)[0]
        return {
            "status": "success",
            "predicted_temperature": float(pred)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# == 5. CHẠY APP ===
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
