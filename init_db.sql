-- creates DB, tables, sample data, triggers, procedure, and views

CREATE DATABASE IF NOT EXISTS smart_parking;
USE smart_parking;

-- 1) Tables
CREATE TABLE IF NOT EXISTS Vehicles (
  Vehicle_ID INT AUTO_INCREMENT PRIMARY KEY,
  Owner_Name VARCHAR(100),
  Type VARCHAR(20),
  Plate_No VARCHAR(30) UNIQUE
);

CREATE TABLE IF NOT EXISTS Parking_Slots (
  Slot_ID INT AUTO_INCREMENT PRIMARY KEY,
  Status VARCHAR(15) DEFAULT 'Available',
  Level INT DEFAULT 1
);

CREATE TABLE IF NOT EXISTS Entry_Exit (
  Entry_ID INT AUTO_INCREMENT PRIMARY KEY,
  Vehicle_ID INT,
  Entry_Time DATETIME DEFAULT CURRENT_TIMESTAMP,
  Exit_Time DATETIME NULL,
  Slot_ID INT,
  FOREIGN KEY (Vehicle_ID) REFERENCES Vehicles(Vehicle_ID),
  FOREIGN KEY (Slot_ID) REFERENCES Parking_Slots(Slot_ID)
);

CREATE TABLE IF NOT EXISTS Payments (
  Pay_ID INT AUTO_INCREMENT PRIMARY KEY,
  Vehicle_ID INT,
  Amount DECIMAL(10,2),
  Date DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (Vehicle_ID) REFERENCES Vehicles(Vehicle_ID)
);

-- 2) Sample data
INSERT INTO Vehicles (Owner_Name, Type, Plate_No) VALUES
('Alice', 'Car', 'KA01AB1234'),
('Bob',   'Car', 'KA02CD5678'),
('Carol', 'Bike','KA03EF9012');

INSERT INTO Parking_Slots (Status, Level) VALUES
('Available',1),('Available',1),('Available',1),('Available',2),('Available',2);

-- 3) Triggers (auto change slot status)
DELIMITER $$
CREATE TRIGGER trg_slot_occupied
AFTER INSERT ON Entry_Exit
FOR EACH ROW
BEGIN
  UPDATE Parking_Slots SET Status = 'Occupied' WHERE Slot_ID = NEW.Slot_ID;
END$$

CREATE TRIGGER trg_slot_available
AFTER UPDATE ON Entry_Exit
FOR EACH ROW
BEGIN
  IF NEW.Exit_Time IS NOT NULL THEN
    UPDATE Parking_Slots SET Status = 'Available' WHERE Slot_ID = NEW.Slot_ID;
  END IF;
END$$
DELIMITER ;

-- 4) Stored Procedure (₹20/hour, min 1 hr)
DELIMITER $$
CREATE PROCEDURE Calculate_Fee(IN in_vehicle_id INT)
BEGIN
  DECLARE v_entry DATETIME;
  DECLARE v_exit DATETIME;
  DECLARE v_hours INT;
  DECLARE v_amount DECIMAL(10,2);

  SELECT Entry_Time, Exit_Time
    INTO v_entry, v_exit
  FROM Entry_Exit
  WHERE Vehicle_ID = in_vehicle_id
  ORDER BY Entry_ID DESC
  LIMIT 1;

  IF v_exit IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Vehicle has not exited yet';
  ELSE
    SET v_hours = GREATEST(1, TIMESTAMPDIFF(HOUR, v_entry, v_exit));
    SET v_amount = v_hours * 20.00;
    INSERT INTO Payments (Vehicle_ID, Amount, Date)
    VALUES (in_vehicle_id, v_amount, NOW());
    SELECT v_hours AS HoursParked, v_amount AS Amount;
  END IF;
END$$
DELIMITER ;

-- 5) Views
CREATE OR REPLACE VIEW Available_Slots AS
SELECT Slot_ID, Level FROM Parking_Slots WHERE Status = 'Available';

CREATE OR REPLACE VIEW Active_Vehicles AS
SELECT v.Vehicle_ID, v.Owner_Name, v.Plate_No, e.Slot_ID, e.Entry_Time
FROM Vehicles v
JOIN Entry_Exit e ON v.Vehicle_ID = e.Vehicle_ID
WHERE e.Exit_Time IS NULL;

CREATE OR REPLACE VIEW Daily_Revenue AS
SELECT DATE(Date) AS TheDate, SUM(Amount) AS Total_Revenue
FROM Payments
GROUP BY DATE(Date);