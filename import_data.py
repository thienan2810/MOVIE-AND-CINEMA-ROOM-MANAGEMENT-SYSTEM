import pandas as pd
import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",
    database="cinemadb"
)

cursor = conn.cursor()

# Read Excel file
file = r"cinema_dataset.xlsx"

customers = pd.read_excel(file, sheet_name="CUSTOMERS")
movies = pd.read_excel(file, sheet_name="MOVIES")
rooms = pd.read_excel(file, sheet_name="CINEMAROOMS")
screenings = pd.read_excel(file, sheet_name="SCREENINGS")
tickets = pd.read_excel(file, sheet_name="TICKETS")

# INSERT CUSTOMERS
for _, row in customers.iterrows():
    cursor.execute(
        "INSERT INTO CUSTOMERS (CustomerName, PhoneNumber) VALUES (%s, %s)",
        (row["CustomerName"], row["PhoneNumber"])
    )

# INSERT MOVIES
for _, row in movies.iterrows():
    cursor.execute(
        "INSERT INTO MOVIES (MovieTitle, Genre, DurationMinutes) VALUES (%s, %s, %s)",
        (row["MovieTitle"], row["Genre"], row["DurationMinutes"])
    )

# INSERT ROOMS
for _, row in rooms.iterrows():
    cursor.execute(
        "INSERT INTO CINEMAROOMS (RoomName, Capacity) VALUES (%s, %s)",
        (row["RoomName"], row["Capacity"])
    )

# INSERT SCREENINGS
for _, row in screenings.iterrows():
    cursor.execute(
        "INSERT INTO SCREENINGS (ScreeningTime, ScreeningDate, MovieID, RoomID) VALUES (%s, %s, %s, %s)",
        (row["ScreeningTime"], row["ScreeningDate"], row["MovieID"], row["RoomID"])
    )

# INSERT TICKETS
for _, row in tickets.iterrows():
    cursor.execute(
        "INSERT INTO TICKETS (SeatNumber, ScreeningID, CustomerID) VALUES (%s, %s, %s)",
        (row["SeatNumber"], row["ScreeningID"], row["CustomerID"])
    )

conn.commit()
cursor.close()
conn.close()

print("Import successful!")
