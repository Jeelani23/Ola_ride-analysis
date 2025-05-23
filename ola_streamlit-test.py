import streamlit as st
import pandas as pd
from PIL import Image
from sqlalchemy import create_engine
from streamlit_option_menu import option_menu
import pymysql

# ---------------------------------------------
# 🚨 One-time upload from CSV to Railway DB
df = pd.read_csv("ola_data.csv")

# Replace with your Railway DB credentials
engine = create_engine("mysql+pymysql://root:ZafVFjlLcsJZwtDHwaXYdSwUEqZMreAC@caboose.proxy.rlwy.net:42869/railway")

# Only run this once during development
try:
    df.to_sql("ola_data", con=engine, if_exists='replace', index=False)
except Exception as e:
    st.warning("Table already exists or error in upload")

# Function to run SQL queries
def run_query(sql):
    return pd.read_sql(sql, con=engine)

# ---------------------------------------------
# Streamlit UI
st.set_page_config(page_title="Ola Ride Data Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center; color: #336699;'>🚖 OLA RIDE DATA ANALYSIS & INSIGHTS</h1>", unsafe_allow_html=True)

# Sidebar menu
with st.sidebar:
    st.image(Image.open("Ola-Cabs-Logo.png"), width=200)  # Ensure this image is in same folder or give path
    select = option_menu("Main Menu", ["🏠 HOME", "📊 Business Insights"])

# HOME PAGE
if select == "🏠 HOME":
    col1, col2 = st.columns(2)

    with col1:
        st.header("About Ola Cabs")
        st.markdown("""
        Ola is one of India’s largest mobility platforms, providing various ride-hailing services including Micro, Mini, Prime, and Auto.
        - ✅ Real-time tracking
        - 💳 Multiple payment options
        - 🧾 Ride history & invoices
        - 🌟 Driver and rider ratings
        """)
        st.link_button("Book Your Ride Now", "https://www.olacabs.com/")

    with col2:
        st.image(Image.open("ola-cabs-01.jpg"), width=600)

# BUSINESS INSIGHTS PAGE
elif select == "📊 Business Insights":
    st.subheader("📌 Select a query to analyze:")

    question = st.selectbox("Choose a business insight", [
        "1. Total Successful Bookings",
        "2. Avg Ride Distance per Vehicle Type",
        "3. Total Rides Cancelled by Customers",
        "4. Top 5 Customers by Ride Count",
        "5. Number of Rides Cancelled by Drivers (Car/Personal Issues)",
        "6. Prime Sedan Ratings (Max/Min)",
        "7. Rides Paid via UPI",
        "8. Avg Customer Rating by Vehicle Type",
        "9. Total Booking Value (Success Only)",
        "10. Incomplete Rides & Reasons"
    ])

    if question == "1. Total Successful Bookings":
        df = run_query("SELECT COUNT(*) AS Successful_Rides FROM ola_data WHERE Booking_Status = 'Success'")
        st.success(f"✅ Total Successful Rides: **{df.iloc[0]['Successful_Rides']}**")

    elif question == "2. Avg Ride Distance per Vehicle Type":
        df = run_query("""
            SELECT Vehicle_Type, ROUND(AVG(Ride_Distance), 2) AS Average_Ride_Distance
            FROM ola_data WHERE Booking_Status = 'Success'
            GROUP BY Vehicle_Type
        """)
        st.dataframe(df, use_container_width=True)

    elif question == "3. Total Rides Cancelled by Customers":
        df = run_query("SELECT COUNT(*) AS Cancelled_By_Customers FROM ola_data WHERE Booking_Status = 'Canceled by Customer'")
        st.error(f"❌ Rides Cancelled by Customers: **{df.iloc[0]['Cancelled_By_Customers']}**")

    elif question == "4. Top 5 Customers by Ride Count":
        df = run_query("""
            SELECT Customer_ID, COUNT(*) AS Number_Of_Rides
            FROM ola_data
            GROUP BY Customer_ID
            ORDER BY Number_Of_Rides DESC
            LIMIT 5
        """)
        st.dataframe(df, use_container_width=True)

    elif question == "5. Number of Rides Cancelled by Drivers (Car/Personal Issues)":
        df = run_query("""
            SELECT COUNT(*) AS Cancelled_By_Drivers
            FROM ola_data
            WHERE Booking_Status = 'Canceled by Driver'
            AND Canceled_Rides_by_Driver = 'Personal & Car related issue'
        """)
        st.warning(f"🧰 Driver-Cancelled Rides (Car/Personal): **{df.iloc[0]['Cancelled_By_Drivers']}**")

    elif question == "6. Prime Sedan Ratings (Max/Min)":
        df = run_query("""
            SELECT MAX(Driver_Ratings) AS Max_Rating, MIN(Driver_Ratings) AS Min_Rating
            FROM ola_data
            WHERE Vehicle_Type = 'Prime Sedan' AND Booking_Status = 'Success'
        """)
        st.metric("🌟 Max Rating", df.iloc[0]['Max_Rating'])
        st.metric("🌑 Min Rating", df.iloc[0]['Min_Rating'])

    elif question == "7. Rides Paid via UPI":
        df = run_query("SELECT * FROM ola_data WHERE Payment_Method = 'UPI'")
        st.dataframe(df, use_container_width=True)
        st.success(f"💸 Total UPI Payments: **{len(df)}**")

    elif question == "8. Avg Customer Rating by Vehicle Type":
        df = run_query("""
            SELECT Vehicle_Type, ROUND(AVG(Customer_Rating), 2) AS Avg_Customer_Rating
            FROM ola_data
            WHERE Booking_Status = 'Success'
            GROUP BY Vehicle_Type
        """)
        st.dataframe(df, use_container_width=True)

    elif question == "9. Total Booking Value (Success Only)":
        df = run_query("""
            SELECT SUM(Booking_Value) AS Total_Booking_Value
            FROM ola_data
            WHERE Booking_Status = 'Success'
        """)
        st.metric("💰 Total Booking Value (₹)", round(df.iloc[0]['Total_Booking_Value'], 2))

    elif question == "10. Incomplete Rides & Reasons":
        df = run_query("SELECT Incomplete_Rides, Incomplete_Rides_Reason FROM ola_data WHERE Incomplete_Rides = 'Yes'")
        st
