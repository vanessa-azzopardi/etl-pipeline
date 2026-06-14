# Extract Transform Load (ETL) Project

# Import libraries
import requests
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import matplotlib.pyplot as plt


# Extract
# Send a request to OpenWeatherMap API and pull weather data for the specified cities
def extract_weather_data(city, api_key):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
                'q': city,
                'appid': api_key,
                'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    return response.json()

# Load API key
load_dotenv()
api_key = os.getenv("OPENWEATHER_API_KEY")

# Extract the weather data for some cities
cities = ['Valletta', 'Santa Venera', 'London', 'Paris', 'New York']
weather_data = [extract_weather_data(city, api_key) for city in cities]
print(weather_data)

#---------------------------------------------------------------------------------

#  Transform
def transform_weather_data(raw_data):
    transformed_data = []      
    for data in raw_data:
        if 'main' in data:    
            city_data = {
                'country': data['sys']['country'],
                'city': data['name'],
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'weather': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed']
            }
            transformed_data.append(city_data)
    return pd.DataFrame(transformed_data)

# Transform the extracted data
weather_df = transform_weather_data(weather_data)
print(weather_df)

#---------------------------------------------------------------------------------

# Load
# Create a SQLite database connection
engine = create_engine('sqlite:///weather_data.db')

# Load the transformed data into SQL table
weather_df.to_sql('weather', con=engine, if_exists='replace', index=False)

print("Data loaded into SQLite successfully!")

# Query the data from the SQLite database
query = "SELECT * FROM weather"

result = pd.read_sql(query, con=engine)
print(result)

#---------------------------------------------------------------------------------

# Visualise
# Visualise the data using Matplotlib

# Plot the temperature data
plt.figure(figsize=(8, 5))
plt.bar(weather_df['city'], weather_df['temperature'], color='blue')
plt.xlabel('City')
plt.ylabel('Temperature (oC)')
plt.title('Temperature Comparison of Cities')
plt.show()






# Weather Data ETL Pipeline

# Import libraries
import os
import matplotlib.pyplot as plt
import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine


def extract_weather_data(city, api_key):
    """
    Extract current weather data for a single city from the OpenWeatherMap API.
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    return response.json()


def transform_weather_data(raw_data):
    """
    Transform raw JSON weather data into a structured pandas DataFrame.
    """
    transformed_data = []

    for data in raw_data:
        if "main" in data:
            city_data = {
                "country": data["sys"]["country"],
                "city": data["name"],
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "weather": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
            }

            transformed_data.append(city_data)

    return pd.DataFrame(transformed_data)

    
def load_to_database(weather_df, database_name="weather_data.db", table_name="weather"):
    """
    Load the transformed weather data into a SQLite database.
    """
    engine = create_engine(f"sqlite:///{database_name}")

    weather_df.to_sql(
        table_name,
        con=engine,
        if_exists="replace",
        index=False,
    )

    return engine


def query_database(engine, table_name="weather"):
    """
    Query the weather table from the SQLite database.
    """
    query = f"SELECT * FROM {table_name}"

    return pd.read_sql(query, con=engine)


def create_visualisation(weather_df, output_path="images/temperature-comparison-chart.png"):
    """
    Create and save a bar chart comparing temperature by city.
    """
    plt.figure(figsize=(8, 5))
    plt.bar(weather_df["city"], weather_df["temperature"])
    plt.xlabel("City")
    plt.ylabel("Temperature (°C)")
    plt.title("Temperature Comparison of Cities")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()


def main():
    """
    Run the full ETL pipeline.
    """
    load_dotenv()

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY not found. Please add it to your .env file.")

    cities = ["Valletta", "Santa Venera", "London", "Paris", "New York"]

    # Extract
    weather_data = [extract_weather_data(city, api_key) for city in cities]

    # Transform
    weather_df = transform_weather_data(weather_data)

    # Save sample output
    weather_df.to_csv("data/sample-output.csv", index=False)

    # Load
    engine = load_to_database(weather_df)

    print("Data loaded into SQLite successfully.")

    # Query
    result = query_database(engine)
    print(result)

    # Visualise
    create_visualisation(weather_df)


if __name__ == "__main__":
    main()
