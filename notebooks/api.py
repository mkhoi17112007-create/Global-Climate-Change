from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import uvicorn
import os

app = FastAPI(
    title="Climate Change API (5 Cities)",
    description="API dự báo biến đổi khí hậu cho 5 thành phố lớn bằng Prophet.",
    version="2.0"
)

# 1. Khai báo cấu trúc dữ liệu nhận từ người dùng (Có thêm 'city')
class PredictionInput(BaseModel):
    city: str
    year: int

# 2. Endpoint xử lý dự báo
@app.post("/predict")
def predict_temperature(data: PredictionInput):
    # Chuẩn hóa tên thành phố để khớp với tên file đã lưu (vd: 'New York' -> 'new_york')
    city_formatted = data.city.replace(" ", "_").lower()
    model_path = f"../model/prophet_{city_formatted}.pkl"

    # Kiểm tra xem mô hình của thành phố này có tồn tại không
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail=f"Không tìm thấy mô hình cho thành phố: {data.city}")

    try:
        # Tải mô hình tương ứng
        model = joblib.load(model_path)

        # Tạo thời gian dự báo cho 12 tháng của năm được yêu cầu
        dates = pd.date_range(start=f"{data.year}-01-01", end=f"{data.year}-12-01", freq='MS')
        input_df = pd.DataFrame({'ds': dates})

        # Thực hiện dự báo
        pred = model.predict(input_df)
        avg_temp = pred['yhat'].mean()

        return {
            "status": "success",
            "city": data.city,
            "year": data.year,
            "predicted_avg_temperature": float(avg_temp),
            "monthly_predictions": pred['yhat'].tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
