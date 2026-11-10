# OLA Ride Analytics

## 1. Project Overview

OLA Ride Analytics is a data analytics project designed to analyse ride booking performance, revenue, vehicle utilisation, cancellations and customer and driver ratings.

The project uses Python, MySQL, Power BI and Streamlit to transform ride booking data into meaningful business insights through interactive dashboards and SQL analysis.

## 2. Project Objectives

- Analyse overall ride booking performance.
- Identify the most frequently booked vehicle types.
- Evaluate revenue generation and payment methods.
- Understand customer and driver cancellation patterns.
- Analyse customer and driver ratings.
- Provide interactive filters and business-level insights.

## 3. Dataset Description

The project uses an OLA ride booking dataset containing:

- Total records: 103,024
- Total columns: 29
- Missing values: 0 (after the documented data checks)
- Duplicate records: 0 (after the documented data checks)

Important fields include Booking ID, Booking Status, Customer ID, Vehicle Type, Pickup Location, Drop Location, Ride Distance, Booking Value, Payment Method, Customer Rating and Driver Ratings.

## 4. Tools and Technologies

| Tool | Purpose |
|---|---|
| Python | Data analysis and application development |
| Pandas | Data cleaning and manipulation |
| MySQL | Database storage and SQL analysis |
| Power BI | Interactive business dashboards |
| Streamlit | Interactive web application |
| Plotly | Interactive data visualisations |

## 5. Project Workflow

1. Dataset inspection and data quality checks.
2. Data cleaning and preparation using Python.
3. Database creation and data storage in MySQL.
4. SQL queries to answer business questions.
5. Dashboard development using Power BI.
6. Interactive application development using Streamlit.
7. Testing filters, search functionality and dashboard KPIs.

## 6. Power BI Dashboard Pages

The Power BI report contains five pages:

1. Overall Dashboard
2. Vehicle Analysis
3. Revenue Analysis
4. Cancellation Analysis
5. Ratings Analysis

## 7. Streamlit Application Features

The Streamlit application includes:

- Five-section dashboard navigation.
- Interactive vehicle type filter.
- Booking status filter.
- Payment method filter.
- Booking ID and Customer ID search.
- KPI cards for business performance.
- Interactive charts using Plotly.
- SQL Query Explorer with 10 predefined business queries.
- MySQL database connectivity.

## 8. Key Business Metrics

The application analyses:

- Total bookings
- Successful rides
- Revenue from successful rides
- Average ride distance
- Vehicle-wise booking performance
- Average booking value
- UPI revenue
- Customer cancellation rate
- Driver cancellation rate
- Average customer rating
- Average driver rating

## 9. SQL Business Analysis

The SQL Query Explorer provides answers to questions related to:

- Successful bookings
- Average ride distance by vehicle type
- Customer cancellations
- Top five customers by booking count
- Driver cancellation reasons
- Driver ratings for Prime Sedan
- UPI bookings
- Average customer rating by vehicle
- Revenue from successful bookings
- Incomplete rides by reason

## 10. How to Run the Streamlit Application

### Requirements

Install the required Python libraries:

```bash
pip install streamlit pandas pymysql plotly
```

### Database Configuration

The application connects to a MySQL database named `ola_ride_analytics` and uses the `ola_bookings` table.

Configure database credentials in:

`.streamlit/secrets.toml`

Do not upload passwords or database credentials to a public repository.

### Run the Application

Open Command Prompt in the project folder and execute:

```bash
python -m streamlit run app.py
```

The application will open in your browser.

## 11. Project Limitation

Power BI report embedding inside Streamlit was not implemented because an eligible organisational Microsoft account was unavailable.

The Power BI report and Streamlit application are maintained separately.

## 12. Conclusion

OLA Ride Analytics demonstrates how SQL, Python, Power BI and Streamlit can be combined to analyse ride booking operations and present business insights through interactive dashboards.

The project provides a practical example of data analysis, database querying, KPI development and business intelligence application development.

---

**Project:** OLA Ride Analytics  
**Category:** Data Analytics / Business Intelligence  
**Technologies:** Python, MySQL, Power BI, Streamlit and Plotly