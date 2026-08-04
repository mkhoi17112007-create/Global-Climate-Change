
import pandas as pd
import numpy as np

#  dữ liệu
df = pd.read_csv('data/raw/GlobalLandTemperaturesByMajorCity.csv')
df['dt'] = pd.to_datetime(df['dt'])

# Lọc một thành phố
city_df = df[df['City'] == 'Tokyo'].copy()
city_df = city_df.set_index('dt').sort_index()

# Đảm bảo trục thời gian liên tục từ năm 1850 đến 2013
full_idx = pd.date_range(start='1850-01-01', end=city_df.index.max(), freq='MS')
city_df = city_df.reindex(full_idx)

# Lấp đầy khoảng trống dữ liệu bằng Nội suy Time/Spline
city_df['AverageTemperature'] = city_df['AverageTemperature'].interpolate(method='time')

# Tạo các đặc trưng thời gian 
city_df['Year'] = city_df.index.year
city_df['Month'] = city_df.index.month
city_df['Lag_1'] = city_df['AverageTemperature'].shift(1)
city_df['Lag_12'] = city_df['AverageTemperature'].shift(12) # Giá trị cùng kỳ năm ngoái
city_df['Rolling_Mean_12'] = city_df['AverageTemperature'].rolling(window=12).mean()

city_df = city_df.dropna()
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV

# Phân chia dữ liệu Train / Test theo mốc thời gian 
train = city_df[city_df['Year'] < 2000]
test = city_df[city_df['Year'] >= 2000]

X_cols = ['Year', 'Month', 'Lag_1', 'Lag_12', 'Rolling_Mean_12']
y_col = 'AverageTemperature'

X_train, y_train = train[X_cols], train[y_col]
X_test, y_test = test[X_cols], test[y_col]

# 1. Mô hình Baseline: Ridge Regression
ridge = Ridge(alpha=1.0)
ridge.fit(X_train, y_train)
pred_ridge = ridge.predict(X_test)

# 2. Mô hình Nâng cao: XGBoost Regressor
xgb = XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=5, random_state=42)
xgb.fit(X_train, y_train)
pred_xgb = xgb.predict(X_test)

# Tối ưu hóa Hyperparameter cho Random Forest / XGBoost bằng GridSearchCV
param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [3, 5, 8],
    'learning_rate': [0.01, 0.05, 0.1]
}
grid_search = GridSearchCV(XGBRegressor(random_state=42), param_grid, cv=3, scoring='neg_mean_squared_error')
grid_search.fit(X_train, y_train)
best_xgb = grid_search.best_estimator_
pred_best_xgb = best_xgb.predict(X_test)

# Bảng đánh giá so sánh kết quả
def evaluate(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    return mae, rmse, r2

metrics = {
    'Ridge Regression': evaluate(y_test, pred_ridge),
    'XGBoost (Baseline)': evaluate(y_test, pred_xgb),
    'XGBoost (Tối ưu GridSearch)': evaluate(y_test, pred_best_xgb)
}

results_df = pd.DataFrame(metrics, index=['MAE (°C)', 'RMSE (°C)', 'R2 Score'])
print(results_df)
# Tạo khung thời gian dự báo 20 năm tới
last_date = city_df.index[-1]
future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=240, freq='MS')

future_predictions = []
current_row = city_df.iloc[-1].copy()

# Vòng lặp dự báo lặp từng tháng
for date in future_dates:
    next_year = date.year
    next_month = date.month
    
    # Cập nhật các đặc trưng
    lag_1 = current_row['AverageTemperature']
    # Giả định lấy lag_12 từ quá khứ gần nhất
    lag_12 = future_predictions[-12] if len(future_predictions) >= 12 else city_df['AverageTemperature'].iloc[-12 + len(future_predictions)]
    rolling_mean = np.mean([lag_1] + future_predictions[-11:]) if len(future_predictions) >= 11 else current_row['Rolling_Mean_12']
    
    X_future = pd.DataFrame([{
        'Year': next_year,
        'Month': next_month,
        'Lag_1': lag_1,
        'Lag_12': lag_12,
        'Rolling_Mean_12': rolling_mean
    }])
    
    pred_temp = best_xgb.predict(X_future)[0]
    future_predictions.append(pred_temp)
    
    # Cập nhật current_row
    current_row['AverageTemperature'] = pred_temp
    current_row['Rolling_Mean_12'] = rolling_mean

# Tạo Series chứa kết quả dự báo 20 năm
future_df = pd.DataFrame({'Forecasted_Temp': future_predictions}, index=future_dates)