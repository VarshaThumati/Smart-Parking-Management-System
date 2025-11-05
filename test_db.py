import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="dbms",          # <-- change if different
    database="smart_parking"
)
print("Connected:", conn.is_connected())

cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM vehicles")
print("Vehicles count:", cur.fetchone()[0])

cur.execute("SELECT Slot_ID, Level FROM available_slots ORDER BY Slot_ID LIMIT 5")
for row in cur.fetchall():
    print("Slot:", row)

cur.close()
conn.close()