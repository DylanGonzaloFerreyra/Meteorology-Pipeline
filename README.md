# Weather Data Pipeline with Apache Airflow 🌤️

This project is an automated data pipeline to fetch weather data using the OpenWeather API, process the data, and store it in a PostgreSQL database. The pipeline is orchestrated using Apache Airflow for scheduling and monitoring tasks.

## Features 🚀
- Fetches real-time weather data for a specified location (default: Buenos Aires, AR).
- Validates and processes the data to include calculated "feels like" temperature.
- Stores the data in a PostgreSQL database for further analysis or visualization.
- Scheduled execution with Apache Airflow (every 5 minutes by default).

---

