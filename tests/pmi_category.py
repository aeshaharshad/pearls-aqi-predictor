from src.utils.aqi_converter import pm25_to_aqi_category

print(pm25_to_aqi_category(45))   # Good
print(pm25_to_aqi_category(120))  # Unhealthy for Sensitive Groups
print(pm25_to_aqi_category(250))  # Very Unhealthy
