import pandas as pd

def process_boxscore_data(dataframe : pd.DataFrame) -> pd.DataFrame:
    if "weather" in dataframe.columns:
        weather_data : dict[int] = process_weather(dataframe["weather"].iloc[0]) 
        dataframe.drop(columns = ["weather"], inplace = True)
    else:
        weather_data = {}

    dataframe["temprature"] = weather_data.get("temprature", None)
    dataframe["wind_speed"] = weather_data.get("wind_speed", None)
    dataframe["humidity"] = weather_data.get("humidity", None)
    dataframe["wind_chill"] = weather_data.get("wind_chill", None)

    dataframe["date"] = pd.to_datetime(dataframe["date"]).dt.date

    dataframe["duration"] = dataframe["duration"].apply(lambda x : int(x.split(":")[0]) * 60 + int(x.split(":")[1]) if type(x) == str else None)
    dataframe["attendance"] = dataframe["attendance"].apply(lambda x : int(x.replace(",",""))) if 'attendance' in dataframe else pd.Series([None])

    return dataframe

def process_weather(weather: str) -> dict[int]:

    weather_data: dict[int] = {}
    for item in weather.split(','):
        if "degrees" in item:
            weather_data["temprature"] = int(item.split(" ")[0])
        elif "mph" in item:
            weather_data["wind_speed"] = int(item.split(" ")[2])
        elif "humidity" in item:
            weather_data["humidity"] = int(item.split(" ")[3][:-1])
        elif "no wind" in item:
            weather_data["wind_speed"] = 0
        elif "wind chill" in item:
            weather_data["wind_chill"] = int(item.split(" ")[3])
        else:
            raise ValueError(f"Unrecognized weather item: {item}")
        
    return weather_data