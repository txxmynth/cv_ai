from datetime import datetime, date, timedelta
import pandas as pd
import requests
import pickle
def get_weather():
    api_key = 'b9bd640eb3b566bc89bf8098669f9cb8'
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q=Columbus,OH,US&appid={api_key}"
    geocode_response = requests.get(geocode_url)

    if geocode_response.status_code != 200:
        print(f'Failed to fetch latitude and longitude, status code: {geocode_response.status_code}')
        if geocode_response.status_code == 401:
            print("Authorization error: Check your API key.")
        return None

    geocode_data = geocode_response.json()
    if not geocode_data:
        print('No location data found.')
        return None

    lat, lon = geocode_data[0]['lat'], geocode_data[0]['lon']

    base_url = "https://api.openweathermap.org/data/3.0/onecall?"
    complete_url = f"{base_url}lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&units=imperial&appid={api_key}"
    response = requests.get(complete_url)

    if response.status_code == 200:
        data = response.json()
        week_weather = []
        for day in data['daily']:
            day_weather = {
                'date': datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d'),
                'temperature': day['temp']['day'],
                'humidity': day['humidity'],
                'weather_description': day['weather'][0]['description']
            }
            week_weather.append(day_weather)
        return week_weather
    else:
        print(f'Failed to fetch weather data, status code: {response.status_code}')
        if response.status_code == 401:
            print("Authorization error: Check your API key.")
        return None
    
def get_holidays(holiday_date=None):
    holiday_list = {
        (10, 25): 'Halloween',
        (11, 11): 'Veteran\'s Day',
        (1, 15): 'Martin Luther King Jr. Day',
        (2, 14): 'Valentine\'s Day',
        (5, 5): 'Cinco de Mayo',
        (10, 8): 'Columbus Day',
        (12, 24): 'Christmas Eve',
        (12, 31): 'New Year\'s Eve'
    }
    if holiday_date is None:
        holiday_date = datetime.now().date()
    month_day = (holiday_date.month, holiday_date.day)
    return holiday_list.get(month_day, None)

def get_events(event_date=None):
    events = {
        date(2024, 8, 31): 'Ohio State Football Gameday',
        date(2024, 9, 7): 'Ohio State Football Gameday',
        date(2024, 9, 21): 'Ohio State Football Gameday',
        date(2024, 9, 28): 'Ohio State Football Gameday',
        date(2024, 10, 5): 'Ohio State Football Gameday',
        date(2024, 10, 12): 'Ohio State Football Gameday',
        date(2024, 10, 26): 'Ohio State Football Gameday',
        date(2024, 11, 2): 'Ohio State Football Gameday',
        date(2024, 11, 9): 'Ohio State Football Gameday',
        date(2024, 11, 16): 'Ohio State Football Gameday',
        date(2024, 11, 23): 'Ohio State Football Gameday',
        date(2024, 11, 30): 'Ohio State Football Gameday',
        date(2025, 6, 13): 'Pride Festival',
        date(2025, 6, 14): 'Pride Festival',
        date(2025, 2, 28): 'Arnold Classic',
        date(2025, 3, 1): 'Arnold Classic',
        date(2025, 3, 2): 'Arnold Classic',
    }
    if event_date is None:
        print('Please add an event date')
        return None
    return events.get(event_date, None)

def get_week_data():
    start_date = datetime.now()
    weather_data = get_weather()
    if not weather_data:
        print("No weather data available.")
        return None
    week_data = {}

    for i in range(7):  # Loop through the next 7 days
        current_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        current_weather = next((item for item in weather_data if item['date'] == current_date), None)

        holiday_data = get_holidays((start_date + timedelta(days=i)).date())
        event_data = get_events((start_date + timedelta(days=i)).date())

        week_data[current_date] = {
            'Average Humidity (%)': current_weather['humidity'] if current_weather else None,
            'Average Temp (°F)': current_weather['temperature'] if current_weather else None,
            'Weather Description': current_weather['weather_description'] if current_weather else None,
            'Holiday': holiday_data,
            'Event': event_data,
            'day_of_week': (start_date + timedelta(days=i)).weekday(),
            'month': (start_date + timedelta(days=i)).month,
            'day': (start_date + timedelta(days=i)).day,
            'year': (start_date + timedelta(days=i)).year
        }
    return week_data

def data_to_df(current_data, feature_names):
    # Create a template DataFrame with zeros
    formatted_data = pd.DataFrame(0, index=[0], columns=feature_names)

    # Fill the DataFrame with current data
    for key, value in current_data.items():
        if key in formatted_data.columns:
            formatted_data[key] = value
            # print(f"Assigned {value} to {key}")

    for col in formatted_data.columns:
        if 'holiday' in col:
            holiday_name = col.replace('holiday_', '')
            formatted_data[col] = 1 if holiday_name == current_data.get('Holiday', '') else 0
            # if formatted_data[col].iloc[0] == 1:
            #     print(f"Assigned 1 to {col} for holiday {holiday_name}")

        elif 'is_' in col:
            event_name = col.replace('is_', '')
            formatted_data[col] = 1 if event_name == current_data.get('Event', '') else 0
            # if formatted_data[col].iloc[0] == 1:
            #     print(f"Assigned 1 to {col} for event {event_name}")

        elif 'Common Weather Description' in col:
            weather_description = col.replace('Common Weather Description_', '')
            formatted_data[col] = 1 if weather_description == current_data.get('Weather Description', '') else 0
            # if formatted_data[col].iloc[0] == 1:
            #     print(f"Assigned 1 to {col} for weather description {weather_description}")

    return formatted_data

def predict_week(model):
    feature_names = model['feature_names']
    current_data = get_week_data()
    if not current_data:
        print("Failed to get week data.")
        return None

    week_predictions = {}
    
    # Converts keys in current_data to datetime objects for reliable manipulation and comparison
    dates = list(current_data.keys())
    dates.sort() 
    
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    for i, date_str in enumerate(dates):
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        label = date_str
        # if date == today:
        #     label = 'today'
        # elif date == tomorrow:
        #     label = 'tomorrow'

        data = current_data[date_str]
        daily_data_df = data_to_df(data, feature_names)  # Prepares my data for a single day
        sales_prediction = model['model_sales'].predict(daily_data_df)[0]
        orders_prediction = model['model_orders'].predict(daily_data_df)[0]
        guests_prediction = model['model_guests'].predict(daily_data_df)[0]

        week_predictions[label] = {
            'sales': sales_prediction,
            'orders': orders_prediction,
            'guests': guests_prediction
        }

    for date, predictions in week_predictions.items():
        print(f"{date}: {predictions}")

    return week_predictions

if __name__ == "__main__":
    model_path = '/Users/Tommy Anthony/OneDrive - Liberty University/Documents/cv_webapp/cv-app/cv_backend/cv_model.pkl'
    with open(model_path, 'rb') as file:
        loaded_model = pickle.load(file)

    predict_week(loaded_model)

