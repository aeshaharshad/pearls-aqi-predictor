# src/utils/aqi_converter.py

def pm25_to_aqi_category(pm25_value):
    """
    Convert PM2.5 value to AQI category code and label.
    
    Returns:
        tuple: (aqi_code:int, aqi_label:str)
    """
    if pm25_value <= 12.0:
        return 1, "Good"
    elif pm25_value <= 35.4:
        return 2, "Moderate"
    elif pm25_value <= 55.4:
        return 3, "Unhealthy for Sensitive Groups"
    elif pm25_value <= 150.4:
        return 4, "Unhealthy"
    elif pm25_value <= 250.4:
        return 5, "Very Unhealthy"
    else:
        return 6, "Hazardous"
