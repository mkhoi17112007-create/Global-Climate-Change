-- 1. Bảng Nhiệt độ theo Quốc gia (GlobalLandTemperaturesByCountry)
CREATE TABLE country_temperatures (
    dt DATE,
    average_temperature REAL,
    average_temperature_uncertainty REAL,
    country VARCHAR(100)
);

-- 2. Bảng Nhiệt độ theo Bang/Tiểu bang (GlobalLandTemperaturesByState)
CREATE TABLE state_temperatures (
    dt DATE,
    average_temperature REAL,
    average_temperature_uncertainty REAL,
    state VARCHAR(100),
    country VARCHAR(100)
);

-- 3. Bảng Nhiệt độ theo Thành phố lớn (GlobalLandTemperaturesByMajorCity)
CREATE TABLE major_city_temperatures (
    dt DATE,
    average_temperature REAL,
    average_temperature_uncertainty REAL,
    city VARCHAR(100),
    country VARCHAR(100),
    latitude VARCHAR(50),
    longitude VARCHAR(50)
);

-- 4. Bảng Nhiệt độ Toàn cầu (GlobalTemperatures)
CREATE TABLE global_temperatures (
    dt DATE,
    land_average_temperature REAL,
    land_average_temperature_uncertainty REAL,
    land_max_temperature REAL,
    land_max_temperature_uncertainty REAL,
    land_min_temperature REAL,
    land_min_temperature_uncertainty REAL,
    land_and_ocean_average_temperature REAL,
    land_and_ocean_average_temperature_uncertainty REAL
);
-- 1. Làm sạch bảng Country
CREATE TABLE country_temp_cleaned AS
SELECT * 
FROM country_temperatures
WHERE average_temperature IS NOT NULL;

-- 2. Làm sạch bảng State
CREATE TABLE state_temp_cleaned AS
SELECT * 
FROM state_temperatures
WHERE average_temperature IS NOT NULL;

-- 3. Làm sạch bảng Major City
CREATE TABLE major_city_temp_cleaned AS
SELECT * 
FROM major_city_temperatures
WHERE average_temperature IS NOT NULL;

-- 4. Làm sạch bảng Global 
-- (Lưu ý: Bảng này sử dụng tên cột là land_average_temperature)
CREATE TABLE global_temp_cleaned AS
SELECT * 
FROM global_temperatures
WHERE land_average_temperature IS NOT NULL;