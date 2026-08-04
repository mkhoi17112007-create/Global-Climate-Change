CREATE TABLE city_temperatures (
    dt DATE,
    average_temperature REAL,
    average_temperature_uncertainty REAL,
    city VARCHAR(100),
    country VARCHAR(100),
    latitude VARCHAR(50),
    longitude VARCHAR(50)
);
-- Tạo một bảng mới chỉ chứa những dòng có dữ liệu nhiệt độ hợp lệ
CREATE TABLE city_temp_cleaned AS
SELECT * 
FROM city_temperatures
WHERE average_temperature IS NOT NULL;