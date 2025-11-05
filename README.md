# Smart-Parking-Management-System
Smart Parking Management System - A system to manage parking slots, vehicle entry/exit, and fee calculation in a smart way.

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













