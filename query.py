import mysql.connector
import streamlit as st

# connection to the database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    port=3306,
    password="",
    database="myDb"
)

# fetching data + column names from the database
def view_all_data():
    c = conn.cursor()   # ✅ new cursor each time
    c.execute("SELECT * FROM atl_3 ORDER BY Id DESC")
    data = c.fetchall()
    colnames = [desc[0] for desc in c.description]
    c.close()  # ✅ close cursor to avoid unread results
    return data, colnames
