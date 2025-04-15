from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import pandas as pd
import psycopg2
import os


# Function to validate data
def validate_data(data):
    try:
        if not data:
            raise ValueError("Data is empty.")
        required_keys = ["main", "weather", "name"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing key {key} in data.")
        temp = data["main"]["temp"]
        if temp < -50 or temp > 50:
            raise ValueError(f"Temperature out of range: {temp}")
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False


# Function to calculate "feels like" temperature
def calculate_feels_like(temp, humidity):
    return temp - (0.1 * humidity)


# Function to get data from the API and save it
def get_and_save_data():
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": "Buenos Aires,AR",
        "appid": API_KEY,  # Default key
        "units": "metric",
    }
    response = requests.get(url, params=params)
    data = response.json()

    if not validate_data(data):
        print("Data is not valid.")
        return

    processed_data = {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "feels_like": calculate_feels_like(data["main"]["temp"], data["main"]["humidity"]),
    }
    df = pd.DataFrame([processed_data])
    print("Processed data:")
    print(df)

    # Save to CSV
    df.to_csv("/tmp/climate_report.csv", mode="w", header=True, index=False)
    print("CSV file created successfully.")

    # Save to PostgreSQL
    save_to_postgresql(df)


# Function to save data to PostgreSQL
def save_to_postgresql(dataframe):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="climate_db",  # New database name
            user=username,
            password=password,
        )
        print("Successfully connected to PostgreSQL.")

        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_report (
            datetime TEXT,
            city TEXT,
            temperature FLOAT,
            humidity INT,
            description TEXT,
            feels_like FLOAT
        )
        """)
        conn.commit()
        print("Table created/verified.")

        for _, row in dataframe.iterrows():
            print("Inserting row:", tuple(row))
            cursor.execute("""
            INSERT INTO weather_report (datetime, city, temperature, humidity, description, feels_like)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, tuple(row))
        conn.commit()
        print("Data saved successfully to PostgreSQL.")

    except Exception as e:
        print(f"Error saving to PostgreSQL: {e}")

    finally:
        cursor.close()
        conn.close()


# DAG
with DAG(
    dag_id="weather_simple_dag",
    start_date=datetime(2023, 1, 1),
    schedule_interval="*/5 * * * *",  # Runs every 5 minutes
    catchup=False,  # Does not execute pending tasks
    params={"key": "value"}  # Example params
) as dag:
    task1 = PythonOperator(
        task_id="fetch_weather_data",
        python_callable=get_and_save_data
    )