
import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px

# --------------------------------
# PAGE CONFIGURATION
# --------------------------------
st.set_page_config(
    page_title="OLA Ride Analytics",
    page_icon="🚕",
    layout="wide"
)

# --------------------------------
# GREY DASHBOARD DESIGN
# --------------------------------
st.markdown("""
<style>

.stApp {
    background-color: #E6E6E6;
    color: #252525;
}

[data-testid="stSidebar"] {
    background-color: #292929;
}

[data-testid="stSidebar"] * {
    color: white;
}

h1, h2, h3 {
    color: #292929;
}

div[data-testid="stMetric"] {
    background-color: #F7F7F7;
    border: 1px solid #BDBDBD;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 1px 2px 5px #BBBBBB;
}

.stAlert {
    border-radius: 10px;
}
/* Remove white header patch */
header[data-testid="stHeader"] {
    background-color: #E6E6E6 !important;
}

/* Match the top toolbar background */
[data-testid="stToolbar"] {
    background-color: #E6E6E6 !important;
}

/* Keep the main dashboard background consistent */
.stApp,
[data-testid="stAppViewContainer"] {
    background-color: #E6E6E6 !important;
}

[data-testid="stMetric"] {
    background-color: #D9F0EC;
    border: 1px solid #9CCFC7;
    padding: 18px;
    border-radius: 12px;
}

[data-testid="stMetricLabel"] {
    color: #276D68;
}

[data-testid="stMetricValue"] {
    color: #155E59;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------
# MYSQL DATABASE CONNECTION
# --------------------------------
@st.cache_data
def load_data():
    data = pd.read_csv("ola_bookings.csv")
    return data

def run_sql_query(query):
    connection = pymysql.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=st.secrets["mysql"]["port"]
    )

    result = pd.read_sql(query, connection)
    connection.close()

    return result

df = load_data()
df["Customer_Rating"] = pd.to_numeric(
    df["Customer_Rating"], errors="coerce"
)

df["Driver_Ratings"] = pd.to_numeric(
    df["Driver_Ratings"], errors="coerce"
)

# --------------------------------
# SIDEBAR NAVIGATION
# --------------------------------
st.sidebar.title("🚕 OLA")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "DASHBOARD MENU",
    [
        "Overall",
        "Vehicle Analysis",
        "Revenue",
        "Cancellation",
        "Ratings"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("OLA Ride Analytics")

# ------------------------------
# INTERACTIVE FILTERS
# ------------------------------

st.sidebar.markdown("---")
st.sidebar.subheader("Ride Filters")

# Vehicle Type Filter
vehicle_options = ["All"] + sorted(df["Vehicle_Type"].dropna().unique().tolist())

selected_vehicle = st.sidebar.selectbox(
    "Vehicle Type",
    vehicle_options
)

# Booking Status Filter
status_options = ["All"] + sorted(df["Booking_Status"].dropna().unique().tolist())

selected_status = st.sidebar.selectbox(
    "Booking Status",
    status_options
)

# Payment Method Filter
payment_options = ["All"] + sorted(df["Payment_Method"].dropna().unique().tolist())

selected_payment = st.sidebar.selectbox(
    "Payment Method",
    payment_options
)

# Search Booking or Customer ID
search_id = st.sidebar.text_input(
    "Search Booking ID / Customer ID"
)

# Apply filters
filtered_df = df.copy()

if selected_vehicle != "All":
    filtered_df = filtered_df[
        filtered_df["Vehicle_Type"] == selected_vehicle
    ]

if selected_status != "All":
    filtered_df = filtered_df[
        filtered_df["Booking_Status"] == selected_status
    ]

if selected_payment != "All":
    filtered_df = filtered_df[
        filtered_df["Payment_Method"] == selected_payment
    ]

if search_id:
    filtered_df = filtered_df[
        filtered_df["Booking_ID"].astype(str).str.contains(search_id, case=False, na=False)
        | filtered_df["Customer_ID"].astype(str).str.contains(search_id, case=False, na=False)
    ]

df = filtered_df
# --------------------------------
# MAIN HEADER
# --------------------------------
st.title("🚕 OLA Ride Analytics")
st.caption("Interactive Ride Booking & Business Performance Analysis")

st.markdown("---")


# --------------------------------
# KPI CALCULATIONS
# --------------------------------

total_bookings = len(df)

successful = df[
    df["Booking_Status"] == "Success"
]

successful_rides = len(successful)

successful_revenue = successful["Booking_Value"].sum()

cancelled_rides = df[
    df["Booking_Status"].isin(
        ["Canceled by Customer", "Canceled by Driver"]
    )
].shape[0]

avg_distance = df["Ride_Distance"].mean()

# --------------------------------
# PAGE CONTENT
# --------------------------------

if page == "Overall":

    st.subheader("Overall Business Performance")
    st.caption("Key performance indicators")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Bookings", f"{total_bookings:,}")
    col2.metric("Successful Rides", f"{successful_rides:,}")
    col3.metric("Successful Revenue", f"₹{successful_revenue / 1000000:.2f}M")

    col4, col5 = st.columns(2)

    col4.metric("Cancelled Rides", f"{cancelled_rides:,}")
    col5.metric("Average Ride Distance", f"{avg_distance:.2f} km")
    st.markdown("---")
    st.subheader("Daily Booking Trend")

    daily_bookings = df.groupby("Date").size().reset_index(name="Bookings")

    fig = px.line(
        daily_bookings,
        x="Date",
        y="Bookings",
        title="Number of Bookings Over Time",
        markers=True
    )

    fig.update_traces(line_color="#800000")
    fig.update_layout(
        plot_bgcolor="#F0F0F0",
        paper_bgcolor="#F0F0F0",
        font_color="#333333"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("💡 Business Insights & Recommendations")

    
    # Dynamic Business Insights based on filtered data
    insights = []

    total = len(df)

    if total > 0:

        # 1. Booking Performance
        successful = (df["Booking_Status"] == "Success").sum()
        success_rate = (successful / total) * 100

        insights.append((
            "📊 Booking Performance",
            f"{success_rate:.2f}% of filtered bookings were successful ({successful:,} out of {total:,}).",
            "Review unsuccessful booking statuses and improve booking fulfilment."
        ))

        # 2. Vehicle Performance
        vehicle_counts = df["Vehicle_Type"].value_counts()

        if not vehicle_counts.empty:
            top_vehicle = vehicle_counts.idxmax()
            top_count = vehicle_counts.max()

            insights.append((
                "🚕 Vehicle Performance",
                f"{top_vehicle} is the most booked vehicle with {top_count:,} bookings.",
                f"Analyse demand for {top_vehicle} and plan vehicle availability accordingly."
            ))
        else:
            insights.append((
                "🚕 Vehicle Performance",
                "No vehicle booking data is available.",
                "Review vehicle data availability."
            ))

        # 3. Payment Preferences
        revenue_df = df[df["Booking_Status"] == "Success"].copy()
        revenue_df["Booking_Value"] = pd.to_numeric(
            revenue_df["Booking_Value"], errors="coerce"
        )

        payment_revenue = revenue_df.groupby(
            "Payment_Method"
        )["Booking_Value"].sum().dropna()

        if not payment_revenue.empty:
            top_payment = payment_revenue.idxmax()
            top_payment_revenue = payment_revenue.max()

            insights.append((
                "💳 Payment Preferences",
                f"{top_payment} generates the highest successful booking revenue: ₹{top_payment_revenue:,.2f}.",
                f"Maintain a smooth {top_payment} payment experience and monitor payment issues."
            ))
        else:
            insights.append((
                "💳 Payment Preferences",
                "No successful booking revenue is available for the selected filters.",
                "Review payment data and successful booking records."
            ))

        # 4. Cancellation Management
        customer_cancelled = (
            df["Booking_Status"] == "Canceled by Customer"
        ).sum()

        driver_cancelled = (
            df["Booking_Status"] == "Canceled by Driver"
        ).sum()

        if customer_cancelled > driver_cancelled:
            cancellation_insight = "Customer cancellations are higher than driver cancellations."
            cancellation_recommendation = "Investigate customer cancellation patterns and improve booking transparency."
        elif driver_cancelled > customer_cancelled:
            cancellation_insight = "Driver cancellations are higher than customer cancellations."
            cancellation_recommendation = "Investigate driver cancellation reasons and improve driver support."
        elif customer_cancelled == driver_cancelled:
            cancellation_insight = "Customer and driver cancellations are equal."
            cancellation_recommendation = "Monitor both cancellation categories to identify improvement opportunities."
        
        insights.append((
            "⚠️ Cancellation Management",
            f"{cancellation_insight} Customer: {customer_cancelled:,}; Driver: {driver_cancelled:,}.",
            cancellation_recommendation
        ))

        # 5. Customer Experience
        customer_rating = pd.to_numeric(
            df["Customer_Rating"], errors="coerce"
        ).mean()

        driver_rating = pd.to_numeric(
            df["Driver_Ratings"], errors="coerce"
        ).mean()

        if pd.notna(customer_rating) and pd.notna(driver_rating):
            if customer_rating < driver_rating:
                rating_insight = "Average customer rating is lower than average driver rating."
                rating_recommendation = "Review customer feedback and identify service improvement areas."
            elif driver_rating < customer_rating:
                rating_insight = "Average driver rating is lower than average customer rating."
                rating_recommendation = "Review driver feedback and identify opportunities to improve service."
            else:
                rating_insight = "Average customer and driver ratings are equal."
                rating_recommendation = "Continue monitoring feedback to maintain service quality."

            rating_insight += (
                f" Customer: {customer_rating:.2f}/5; "
                f"Driver: {driver_rating:.2f}/5."
            )
        else:
            rating_insight = "Rating information is unavailable for the selected data."
            rating_recommendation = "Collect and monitor sufficient rating feedback."

        insights.append((
            "⭐ Customer Experience",
            rating_insight,
            rating_recommendation
        ))

    else:
        insights.append((
            "📊 No Data Available",
            "No bookings match the selected filters.",
            "Change or clear the filters to view business insights."
        ))

    # Display teal insight panels
    for title, insight, recommendation in insights:
        st.markdown(
            f"""
            <div style="
                background-color: #D9F0EC;
                padding: 18px;
                border-radius: 12px;
                border-left: 5px solid #276D68;
                margin-bottom: 12px;
            ">
                <h4 style="color:#155E59; margin:0 0 10px 0;">
                    {title}
                </h4>
                <p style="color:#276D68; margin:0 0 8px 0;">
                    <b>Insight:</b> {insight}
                </p>
                <p style="color:#155E59; margin:0;">
                    <b>Recommendation:</b> {recommendation}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

elif page == "Vehicle Analysis":

    st.subheader("Vehicle Performance KPIs")

    vehicle_counts = df["Vehicle_Type"].value_counts()

    if not vehicle_counts.empty:
        most_booked = vehicle_counts.idxmax()
    else:
        most_booked = "N/A"

    avg_value = df.groupby("Vehicle_Type")["Booking_Value"].mean()

    if not avg_value.empty:
        highest_value = avg_value.max()
    else:
        highest_value = 0

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Most Booked Vehicle", most_booked)

    with col2:
        st.metric("Highest Average Booking Value", f"₹{highest_value:,.2f}")

    st.subheader("Vehicle Analysis")

    st.markdown("---")
    st.subheader("Vehicle Bookings by Type")

    vehicle_bookings = df["Vehicle_Type"].value_counts().reset_index()
    vehicle_bookings.columns = ["Vehicle Type", "Bookings"]

    fig_vehicle = px.bar(
        vehicle_bookings,
        x="Vehicle Type",
        y="Bookings",
        title="Total Bookings by Vehicle Type",
        color_discrete_sequence=["#800000"]
    )

    fig_vehicle.update_layout(
        plot_bgcolor="#F0F0F0",
        paper_bgcolor="#F0F0F0",
        font_color="#333333"
    )

    st.plotly_chart(fig_vehicle, use_container_width=True)

    st.subheader("Average Ride Distance by Vehicle Type")

    avg_distance = df.groupby("Vehicle_Type")["Ride_Distance"].mean().reset_index()
    avg_distance.columns = ["Vehicle Type", "Average Distance"]

    fig_distance = px.bar(
        avg_distance,
        x="Vehicle Type",
        y="Average Distance",
        title="Average Ride Distance (KM)",
        color_discrete_sequence=["#800000"]
    )

    fig_distance.update_layout(
        plot_bgcolor="#F0F0F0",
        paper_bgcolor="#F0F0F0",
        font_color="#333333"
    )

    st.plotly_chart(fig_distance, use_container_width=True)
    st.subheader("Successful Rides by Vehicle Type")

    success_by_vehicle = df[df["Booking_Status"] == "Success"].groupby("Vehicle_Type").size().reset_index(name="Successful Rides")

    fig_success = px.bar(
        success_by_vehicle,
        x="Vehicle_Type",
        y="Successful Rides",
        title="Successful Rides by Vehicle Type",
        color_discrete_sequence=["#800000"]
    )

    fig_success.update_layout(
        plot_bgcolor="#F0F0F0",
        paper_bgcolor="#F0F0F0",
        font_color="#333333"
    )

    st.plotly_chart(fig_success, use_container_width=True)
    st.subheader("Cancellation Rate by Vehicle Type")

    cancellation_data = df[
        df["Booking_Status"].isin(["Canceled by Customer", "Canceled by Driver"])
    ].groupby("Vehicle_Type").size().reset_index(name="Cancelled Rides")

    total_by_vehicle = df.groupby("Vehicle_Type").size().reset_index(name="Total Rides")

    cancellation_data = cancellation_data.merge(total_by_vehicle, on="Vehicle_Type")

    cancellation_data["Cancellation Rate"] = (
        cancellation_data["Cancelled Rides"] / cancellation_data["Total Rides"] * 100
    )

    fig_cancel = px.bar(
        cancellation_data,
        x="Vehicle_Type",
        y="Cancellation Rate",
        title="Cancellation Rate by Vehicle Type (%)",
        color_discrete_sequence=["#800000"]
    )

    st.plotly_chart(fig_cancel, use_container_width=True)
    st.subheader("Average Booking Value by Vehicle Type")

    avg_booking_value = (
        df.groupby("Vehicle_Type")["Booking_Value"]
        .mean()
        .reset_index()
    )

    avg_booking_value.columns = ["Vehicle_Type", "Average Booking Value"]

    fig_value = px.bar(
        avg_booking_value,
        x="Vehicle_Type",
        y="Average Booking Value",
        title="Average Booking Value by Vehicle Type",
        color_discrete_sequence=["#800000"]
    )

    st.plotly_chart(fig_value, use_container_width=True)

elif page == "Revenue":

    st.subheader("Revenue Performance KPIs")

    successful_df = df[df["Booking_Status"] == "Success"]

    avg_success_value = successful_df["Booking_Value"].mean()

    upi_revenue = successful_df.loc[
        successful_df["Payment_Method"] == "UPI",
        "Booking_Value"
    ].sum()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Average Successful Booking Value",
            f"₹{avg_success_value:,.2f}" if pd.notna(avg_success_value) else "₹0.00"
        )

    with col2:
        st.metric("UPI Revenue", f"₹{upi_revenue:,.2f}")

    st.subheader("Revenue Analysis")

    st.subheader("Revenue by Payment Method")

    revenue_data = df[df["Booking_Status"] == "Success"]

    payment_revenue = (
        revenue_data.groupby("Payment_Method")["Booking_Value"]
        .sum()
        .reset_index()
    )

    fig_revenue = px.treemap(
        payment_revenue,
        path=["Payment_Method"],
        values="Booking_Value",
        color="Booking_Value",
        color_continuous_scale=["#DBEAFE", "#0F766E", "#172554"],
        title="Successful Revenue by Payment Method"
    )

    st.plotly_chart(fig_revenue, use_container_width=True)

    st.subheader("Revenue Contribution by Vehicle Type")

    vehicle_revenue = (
        revenue_data.groupby("Vehicle_Type")["Booking_Value"]
        .sum()
        .reset_index()
    )

    fig_vehicle_revenue = px.pie(
        vehicle_revenue,
        names="Vehicle_Type",
        values="Booking_Value",
        hole=0.55,
        title="Successful Revenue Share by Vehicle",
        color_discrete_sequence=[
            "#172554",
            "#0F766E",
            "#F59E0B",
            "#C2415D",
            "#8B5CF6",
            "#0891B2",
            "#64748B"
        ]
    )

    st.plotly_chart(fig_vehicle_revenue, use_container_width=True)

    st.subheader("Daily Revenue Trend")

    daily_revenue = revenue_data.copy()

    daily_revenue["Date"] = pd.to_datetime(
        daily_revenue["Date"]
    ).dt.date

    daily_revenue = (
        daily_revenue.groupby("Date")["Booking_Value"]
        .sum()
        .reset_index()
    )

    fig_daily = px.area(
        daily_revenue,
        x="Date",
        y="Booking_Value",
        title="Daily Successful Revenue",
        color_discrete_sequence=["#0F766E"],
        markers=True
    )

    fig_daily.update_traces(
        fill="tozeroy",
        line=dict(width=3)
    )

    st.plotly_chart(fig_daily, use_container_width=True)

    st.subheader("Revenue Ranking by Vehicle")

    vehicle_revenue = (
        revenue_data.groupby("Vehicle_Type")["Booking_Value"]
        .sum()
        .reset_index()
        .sort_values("Booking_Value")
    )

    fig_rank = px.bar(
        vehicle_revenue,
        x="Booking_Value",
        y="Vehicle_Type",
        orientation="h",
        title="Successful Revenue Ranking",
        color="Booking_Value",
        color_continuous_scale=["#F59E0B", "#0F766E", "#172554"],
        text_auto=".2s"
    )

    fig_rank.update_layout(
        yaxis_title="Vehicle Type",
        xaxis_title="Successful Revenue (₹)"
    )

    st.plotly_chart(fig_rank, use_container_width=True)

elif page == "Cancellation":

    st.subheader("Cancellation Performance KPIs")

    total_bookings = len(df)

    customer_cancelled = (
        df["Booking_Status"] == "Canceled by Customer"
    ).sum()

    driver_cancelled = (
        df["Booking_Status"] == "Canceled by Driver"
    ).sum()

    customer_cancel_rate = (
        customer_cancelled / total_bookings * 100
        if total_bookings > 0 else 0
    )

    driver_cancel_rate = (
        driver_cancelled / total_bookings * 100
        if total_bookings > 0 else 0
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Customer Cancellation Rate",
            f"{customer_cancel_rate:.2f}%"
        )

    with col2:
        st.metric(
            "Driver Cancellation Rate",
            f"{driver_cancel_rate:.2f}%"
        )
    st.subheader("Cancellation Analysis")

    # Cancellation Responsibility
    st.markdown("---")
    st.subheader("Customer vs Driver Cancellations")

    cancel_data = df[
        df["Booking_Status"].isin(
            ["Canceled by Customer", "Canceled by Driver"]
        )
    ]

    cancel_summary = (
        cancel_data["Booking_Status"]
        .value_counts()
        .reset_index()
    )

    cancel_summary.columns = [
        "Cancellation Type",
        "Bookings"
    ]

    fig_cancel = px.bar(
        cancel_summary,
        x="Bookings",
        y="Cancellation Type",
        orientation="h",
        color="Cancellation Type",
        color_discrete_map={
            "Canceled by Customer": "#800000",
            "Canceled by Driver": "#E6A23C"
        },
        text="Bookings",
        title="Customer vs Driver Cancellations"
    )

    fig_cancel.update_layout(
        plot_bgcolor="#F8F5F2",
        paper_bgcolor="#F8F5F2",
        font_color="#333333",
        showlegend=False,
        height=450
    )

    st.plotly_chart(
        fig_cancel,
        use_container_width=True
    )
    # Customer Cancellation Reasons
    st.markdown("---")
    st.subheader("Customer Cancellation Reasons")

    customer_reason = (
        df["Canceled_Rides_by_Customer"]
        .dropna()
        .astype(str)
    )

    customer_reason = customer_reason[
        ~customer_reason.str.strip().isin(["", "nan", "Not Applicable"])
    ]

    customer_summary = (
        customer_reason.value_counts()
        .reset_index()
    )

    customer_summary.columns = ["Cancellation Reason", "Bookings"]

    fig_customer_reason = px.bar(
        customer_summary,
        x="Bookings",
        y="Cancellation Reason",
        orientation="h",
        color="Bookings",
        title="Reasons for Customer Cancellations"
    )

    st.plotly_chart(
        fig_customer_reason,
        use_container_width=True
    )

    # Driver Cancellation Reasons
    st.markdown("---")
    st.subheader("Driver Cancellation Reasons")

    driver_reason = (
        df["Canceled_Rides_by_Driver"]
        .dropna()
        .astype(str)
    )

    driver_reason = driver_reason[
        ~driver_reason.str.strip().isin(["", "nan", "Not Applicable"])
    ]

    driver_summary = (
        driver_reason.value_counts()
        .reset_index()
    )

    driver_summary.columns = ["Cancellation Reason", "Bookings"]

    fig_driver_reason = px.bar(
        driver_summary,
        x="Bookings",
        y="Cancellation Reason",
        orientation="h",
        color="Bookings",
        title="Reasons for Driver Cancellations"
    )

    st.plotly_chart(
        fig_driver_reason,
        use_container_width=True
    )

elif page == "Ratings":

    st.subheader("Rating Performance KPIs")

    # Convert ratings into numeric values
    df["Customer_Rating"] = pd.to_numeric(
        df["Customer_Rating"], errors="coerce"
    )

    df["Driver_Ratings"] = pd.to_numeric(
        df["Driver_Ratings"], errors="coerce"
    )

    # Calculate average ratings
    avg_customer_rating = df["Customer_Rating"].mean()
    avg_driver_rating = df["Driver_Ratings"].mean()

    # KPI cards
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Average Customer Rating",
            f"{avg_customer_rating:.2f}/5"
            if pd.notna(avg_customer_rating) else "N/A"
        )

    with col2:
        st.metric(
            "Average Driver Rating",
            f"{avg_driver_rating:.2f}/5"
            if pd.notna(avg_driver_rating) else "N/A"
        )

    # CHART 1: Customer and Driver Ratings
    st.subheader("Customer and Driver Ratings")
    st.markdown("---")

    rating_data = (
        df.groupby("Vehicle_Type")[
            ["Customer_Rating", "Driver_Ratings"]
        ]
        .mean()
        .reset_index()
    )

    rating_data = rating_data.melt(
        id_vars="Vehicle_Type",
        value_vars=["Customer_Rating", "Driver_Ratings"],
        var_name="Rating Type",
        value_name="Average Rating"
    )

    fig_rating = px.bar(
        rating_data,
        x="Vehicle_Type",
        y="Average Rating",
        color="Rating Type",
        barmode="group",
        title="Customer vs Driver Ratings",
        color_discrete_sequence=["#E6A23C", "#245B8F"]
    )

    st.plotly_chart(
        fig_rating,
        use_container_width=True,
        theme=None
    )

    # CHART 2: Average Customer Rating by Vehicle
    st.subheader("Average Customer Rating by Vehicle Type")

    customer_rating = (
        df.groupby("Vehicle_Type")["Customer_Rating"]
        .mean()
        .reset_index()
    )

    fig_customer = px.bar(
        customer_rating,
        x="Vehicle_Type",
        y="Customer_Rating",
        color="Customer_Rating",
        color_continuous_scale="YlOrBr",
        title="Average Customer Rating"
    )

    st.plotly_chart(
        fig_customer,
        use_container_width=True,
        theme=None
    )

    # CHART 3: Average Driver Rating by Vehicle
    st.subheader("Average Driver Rating by Vehicle Type")

    driver_rating = (
        df.groupby("Vehicle_Type")["Driver_Ratings"]
        .mean()
        .reset_index()
    )

    fig_driver = px.bar(
        driver_rating,
        x="Vehicle_Type",
        y="Driver_Ratings",
        color="Driver_Ratings",
        color_continuous_scale="Blues",
        title="Average Driver Rating"
    )

    st.plotly_chart(
        fig_driver,
        use_container_width=True,
        theme=None
    )

    # CHART 4: Customer Rating Distribution
    st.subheader("Customer Rating Distribution")

    rating_distribution = (
        df["Customer_Rating"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    rating_distribution.columns = ["Rating", "Count"]

    fig_distribution = px.bar(
        rating_distribution,
        x="Rating",
        y="Count",
        color="Count",
        color_continuous_scale="YlOrBr",
        title="Distribution of Customer Ratings"
    )

    st.plotly_chart(
        fig_distribution,
        use_container_width=True,
        theme=None
    )


    st.markdown("---")
st.subheader("Booking Status Breakdown")

status_data = df["Booking_Status"].value_counts().reset_index()
status_data.columns = ["Booking Status", "Bookings"]

fig2 = px.pie(
    status_data,
    names="Booking Status",
    values="Bookings",
    hole=0.45,
    title="Booking Status Distribution",
    color_discrete_sequence=[
        "#800000", "#A52A2A", "#D9D9D9", "#666666"
    ]
)

fig2.update_layout(
    plot_bgcolor="#F0F0F0",
    paper_bgcolor="#F0F0F0",
    font_color="#333333"
)

st.plotly_chart(fig2, use_container_width=True)

# SQL QUERY EXPLORER

st.markdown("---")
st.header("SQL Query Explorer")

sql_questions = {
    "Successful Bookings":
        """SELECT * FROM ola_bookings
        WHERE Booking_Status = 'Success'""",

    "Average Ride Distance by Vehicle":
        """SELECT Vehicle_Type,
        AVG(Ride_Distance) AS Average_Distance
        FROM ola_bookings
        GROUP BY Vehicle_Type""",

    "Customer Cancellations":
        """SELECT COUNT(*) AS Customer_Cancellations
        FROM ola_bookings
        WHERE Booking_Status = 'Canceled by Customer'""",

    "Top 5 Customers":
        """SELECT Customer_ID, COUNT(*) AS Total_Rides
        FROM ola_bookings
        GROUP BY Customer_ID
        ORDER BY Total_Rides DESC LIMIT 5""",

    "Driver Cancellations":
        """SELECT COUNT(*) AS Total_Cancellations
        FROM ola_bookings
        WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue'""",

    "Driver Ratings for Prime Sedan":
        """SELECT MAX(Driver_Ratings) AS Maximum_Rating,
        MIN(Driver_Ratings) AS Minimum_Rating
        FROM ola_bookings
        WHERE Vehicle_Type = 'Prime Sedan'""",

    "UPI Bookings":
        """SELECT COUNT(*) AS UPI_Bookings
        FROM ola_bookings
        WHERE Payment_Method = 'UPI'""",

    "Average Customer Rating":
        """SELECT Vehicle_Type,
        AVG(Customer_Rating) AS Average_Rating
        FROM ola_bookings
        GROUP BY Vehicle_Type""",

    "Successful Booking Revenue":
        """SELECT SUM(Booking_Value) AS Successful_Revenue
        FROM ola_bookings
        WHERE Booking_Status = 'Success'""",

    "Incomplete Rides":
        """SELECT Incomplete_Rides_Reason,
        COUNT(*) AS Total_Rides
        FROM ola_bookings
        WHERE Incomplete_Rides = TRUE
        GROUP BY Incomplete_Rides_Reason"""
}
st.subheader("SQL Query Explorer")

selected_question = st.selectbox(
    "Choose a SQL business question",
    list(sql_questions.keys())
)

if st.button("Run SQL Query"):
    query = sql_questions[selected_question]

    try:
        connection = pymysql.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            port=st.secrets["mysql"]["port"]
        )

        result = pd.read_sql(query, connection)
        connection.close()

        st.dataframe(result, use_container_width=True)

    except Exception as e:
        st.error(f"Query error: {e}")