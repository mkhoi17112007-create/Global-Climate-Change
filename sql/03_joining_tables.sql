-- Gộp dữ liệu nhiệt độ thành phố và quốc gia theo ngày và tên quốc gia
CREATE TABLE city_country_joined AS
SELECT 
    city_tbl.dt,
    city_tbl.city,
    city_tbl.country,
    city_tbl.average_temperature AS city_temp,
    country_tbl.average_temperature AS country_temp,
    city_tbl.latitude,
    city_tbl.longitude
FROM city_temp_cleaned AS city_tbl
LEFT JOIN country_temp_cleaned AS country_tbl 
    ON city_tbl.country = country_tbl.country 
    AND city_tbl.dt = country_tbl.dt;