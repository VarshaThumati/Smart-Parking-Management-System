# Smart Parking Management System

## 🎯 Project Overview  
This system is designed to automate parking slot management by tracking vehicle entry and exit, managing slot occupancy, and computing parking fees in real time. It’s a practical, real‑world application ideal for demonstrating major database concepts.

---

## 🧩 Key Entities  
- **Vehicles**: Vehicle_ID, Owner_Name, Type, Plate_No  
- **Parking_Slots**: Slot_ID, Status (Available/Occupied), Level  
- **Entry_Exit**: Entry_ID, Vehicle_ID, Entry_Time, Exit_Time, Slot_ID  
- **Payments**: Pay_ID, Vehicle_ID, Amount, Date  

---

## 📚 DBMS Concepts Demonstrated  
- **Triggers**: Automatically mark slots as *Occupied* when a vehicle enters and *Available* when it exits.  
- **Stored Procedures**: Calculate parking fees based on duration and record payment.  
- **Views**:  
  - `Available_Slots` - shows all free slots  
  - `Active_Vehicles` - vehicles currently parked  
  - `Daily_Revenue` - revenue summary by date  
- **Joins**: Relate tables such as Vehicles + Entry_Exit + Payments + Parking_Slots to produce combined reports.

Checking the database connection is established or not:

<img width="995" height="326" alt="image" src="https://github.com/user-attachments/assets/797e7f30-fb9a-4b0a-8b65-470e1e499221" />

Initial stage of Parking Dashboard:

<img width="1233" height="823" alt="image" src="https://github.com/user-attachments/assets/01656e70-c317-421f-a46d-39a62070a7b9" />

<img width="1233" height="810" alt="image" src="https://github.com/user-attachments/assets/557f09e5-ca1c-4531-811b-39fc970e1b70" />

<img width="1916" height="971" alt="image" src="https://github.com/user-attachments/assets/b64aed5a-74ae-45c9-8996-0a807bef25fe" />

Explaining Schema & Concepts:

We manage vehicles, slots, and each parking session (entry_exit). Payments store calculated fees.

<img width="953" height="951" alt="image" src="https://github.com/user-attachments/assets/115e11fd-6dc3-4269-925d-e969bb172c83" />

<img width="1030" height="519" alt="image" src="https://github.com/user-attachments/assets/9bbbbf46-f6e7-4e34-b89a-2af9b4944bbd" />

Triggers in action:

These triggers update slot status automatically on insert/update.

<img width="1058" height="947" alt="image" src="https://github.com/user-attachments/assets/9e4d59ab-bcb9-467d-9239-aa585f60fe9c" />

<img width="1030" height="514" alt="image" src="https://github.com/user-attachments/assets/8a96f6c0-d787-476b-8d39-8f69582ec487" />

Stored procedure & views:

Procedure computes duration x rate and inserts into Payments. Views give simple dashboards.

<img width="846" height="940" alt="image" src="https://github.com/user-attachments/assets/71803790-15bd-4804-bb86-17d86a67c7b7" />

Demo using GUI:

The GUI uses the same database.

<img width="1918" height="1019" alt="image" src="https://github.com/user-attachments/assets/ab540cf7-2229-4731-b489-8f9d4358beff" />

<img width="1918" height="986" alt="image" src="https://github.com/user-attachments/assets/73b89342-c6bf-4205-816f-13f324372407" />

<img width="1914" height="966" alt="image" src="https://github.com/user-attachments/assets/f007c4f3-36a3-46a9-9350-7137c301305e" />

<img width="1916" height="969" alt="image" src="https://github.com/user-attachments/assets/6e60ccd5-1ad9-477f-abb1-1d86d7106b0c" />

<img width="1918" height="971" alt="image" src="https://github.com/user-attachments/assets/9b547cf6-8f57-4072-b958-b51833e491ae" />

<img width="1915" height="963" alt="image" src="https://github.com/user-attachments/assets/dbab2a59-fa3b-4fd6-bc7c-8a8e2f505721" />

<img width="1915" height="989" alt="image" src="https://github.com/user-attachments/assets/873c99b6-1126-4419-b5f5-9e803e557c63" />

























