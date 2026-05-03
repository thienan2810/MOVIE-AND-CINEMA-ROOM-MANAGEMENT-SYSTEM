import mysql.connector
import re

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",
    database="CinemaDB"
)
cursor = conn.cursor()

# ===================== HELPERS =====================
def get_room_capacity(screening_id):
    cursor.execute("""
        SELECT cr.Capacity FROM SCREENINGS s
        JOIN CINEMAROOMS cr ON s.RoomID = cr.RoomID
        WHERE s.ScreeningID = %s
    """, (screening_id,))
    result = cursor.fetchone()
    return result[0] if result else None

# ===================== SEAT DISPLAY =====================
def show_seats(screening_id):
    capacity = get_room_capacity(screening_id)
    if capacity is None:
        print("❌ Screening not found!")
        return
 
    num_rows = capacity // 10
    row_labels = [chr(ord('A') + i) for i in range(num_rows)]
 
    cursor.execute("""
        SELECT SeatNumber FROM TICKETS
        WHERE ScreeningID = %s
    """, (screening_id,))
    booked_seats = {row[0] for row in cursor.fetchall()}
 
    print(f"\n=== SEAT MAP (Capacity: {capacity}) ===")
 
    header = "    "
    for c in range(1, 11):
        header += f"{c:^4}"
        if c == 5:
            header += "   "
    print(header)
 
    for r in row_labels:
        line = f"{r}   "
        for c in range(1, 11):
            seat = f"{r}{c}"
            symbol = "[X]" if seat in booked_seats else "[O]"
            line += f"{symbol:^4}"
            if c == 5:
                line += "   "
        print(line)
 
    print("\n[O] = Available  [X] = Booked\n")

# ===================== VALIDATION =====================
def is_valid_seat(seat, num_rows):
    max_row = chr(ord('A') + num_rows - 1)
    pattern = rf'^[A-{max_row}](10|[1-9])$'
    return bool(re.match(pattern, seat))

# ===================== CHECK SEAT =====================
def is_seat_available(screening_id, seat):
    cursor.execute("""
        SELECT * FROM TICKETS
        WHERE ScreeningID = %s AND SeatNumber = %s
    """, (screening_id, seat))
    return cursor.fetchone() is None

# ===================== BOOKING =====================
def book_ticket(customer_id, screening_id, seat):
    seat = seat.upper()
 
    capacity = get_room_capacity(screening_id)
    if capacity is None:
        print("❌ Screening not found!")
        return
 
    num_rows = capacity // 10
 
    if not is_valid_seat(seat, num_rows):
        max_row = chr(ord('A') + num_rows - 1)
        print(f"❌ Invalid seat! Valid rows: A-{max_row}, cols: 1-10 (Example: A5)")
        return
 
    if not is_seat_available(screening_id, seat):
        print("❌ Seat already booked!")
        return
 
    cursor.execute("""
        INSERT INTO TICKETS (CustomerID, ScreeningID, SeatNumber)
        VALUES (%s, %s, %s)
    """, (customer_id, screening_id, seat))
 
    conn.commit()
    print("✅ Ticket booked successfully!")

# ===================== CANCEL =====================
def cancel_ticket(customer_id, screening_id, seat):
    seat = seat.upper()
 
    cursor.execute("""
        DELETE FROM TICKETS
        WHERE CustomerID = %s AND ScreeningID = %s AND SeatNumber = %s
    """, (customer_id, screening_id, seat))
 
    if cursor.rowcount == 0:
        print("❌ Ticket not found!")
    else:
        conn.commit()
        print("✅ Ticket cancelled!")

# ===================== REPORT =====================
def screening_summary():
    cursor.execute("""
        SELECT s.ScreeningID, COUNT(t.TicketID) as tickets, COUNT(t.TicketID) * 55000 as revenue
        FROM SCREENINGS s
        LEFT JOIN TICKETS t ON s.ScreeningID = t.ScreeningID
        GROUP BY s.ScreeningID
        ORDER BY s.ScreeningID
    """)
 
    rows = cursor.fetchall()
    total_tickets = sum(r[1] for r in rows)
    total_revenue = sum(r[2] for r in rows)
 
    print(f"\n{'Screening':<12} {'Tickets':>8} {'Revenue':>18}")
    print("-" * 40)
 
    for sid, tickets, revenue in rows:
        print(f"{sid:<12} {tickets:>8} {revenue:>15,} VND")
 
    print("-" * 40)
    print(f"{'TOTAL':<12} {total_tickets:>8} {total_revenue:>15,} VND\n")

# ===================== UI =====================
def menu():
    while True:
        print("\n=== CINEMA SYSTEM ===")
        print("1. Show Seats")
        print("2. Book Ticket")
        print("3. Cancel Ticket")
        print("4. View Reports")
        print("5. Exit")
 
        choice = input("Choose: ")
 
        if choice == "1":
            try:
                sid = int(input("Screening ID: "))
                show_seats(sid)
            except ValueError:
                print("❌ Invalid input!")
 
        elif choice == "2":
            try:
                cid = int(input("Customer ID: "))
                sid = int(input("Screening ID: "))
 
                show_seats(sid)
                seat = input("Choose seat: ").upper()
 
                book_ticket(cid, sid, seat)
                show_seats(sid)  # refresh
            except ValueError:
                print("❌ Invalid input!")
 
        elif choice == "3":
            try:
                cid = int(input("Customer ID: "))
                sid = int(input("Screening ID: "))
                seat = input("Seat: ")
 
                cancel_ticket(cid, sid, seat)
                show_seats(sid)
            except ValueError:
                print("❌ Invalid input!")
 
        elif choice == "4":
            screening_summary()
 
        elif choice == "5":
            print("Goodbye!")
            break
 
        else:
            print("❌ Invalid choice!")

# ===================== RUN =====================
if __name__ == "__main__":
    menu()