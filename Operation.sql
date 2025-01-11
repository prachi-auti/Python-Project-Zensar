-- Create Database
CREATE DATABASE EventHallDB;
USE EventHallDB;

-- Create Tables
CREATE TABLE Event_Halls (
    Hall_ID INT PRIMARY KEY AUTO_INCREMENT,
    Hall_Name VARCHAR(50),
    Capacity INT,
    Location VARCHAR(100)
);

CREATE TABLE Customers (
    Customer_ID INT PRIMARY KEY AUTO_INCREMENT,
    Customer_Name VARCHAR(50),
    Contact_Number VARCHAR(15),
    Email VARCHAR(100)
);

CREATE TABLE Bookings (
    Booking_ID INT PRIMARY KEY AUTO_INCREMENT,
    Hall_ID INT,
    Customer_ID INT,
    Event_Date DATE,
    Booking_Status VARCHAR(20) DEFAULT 'Pending',
    UNIQUE (Hall_ID, Event_Date),
    FOREIGN KEY (Hall_ID) REFERENCES Event_Halls(Hall_ID),
    FOREIGN KEY (Customer_ID) REFERENCES Customers(Customer_ID)
);

-- Insert Values into Event_Halls
INSERT INTO Event_Halls (Hall_Name, Capacity, Location) VALUES ('Grand Ballroom', 300, 'Downtown');
INSERT INTO Event_Halls (Hall_Name, Capacity, Location) VALUES ('Conference Hall A', 100, 'Midtown');
INSERT INTO Event_Halls (Hall_Name, Capacity, Location) VALUES ('Banquet Hall', 200, 'Uptown');

-- Insert Values into Customers
INSERT INTO Customers (Customer_Name, Contact_Number, Email) VALUES ('John Doe', '9876543210', 'john.doe@example.com');
INSERT INTO Customers (Customer_Name, Contact_Number, Email) VALUES ('Jane Smith', '9123456789', 'jane.smith@example.com');
INSERT INTO Customers (Customer_Name, Contact_Number, Email) VALUES ('Alice Brown', '9812345678', 'alice.brown@example.com');

-- Trigger to Prevent Double Booking
DELIMITER //
CREATE TRIGGER Prevent_Double_Booking
BEFORE INSERT ON Bookings
FOR EACH ROW
BEGIN
    IF EXISTS (
        SELECT 1 FROM Bookings
        WHERE Hall_ID = NEW.Hall_ID AND Event_Date = NEW.Event_Date
    ) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Hall is already booked for the selected date.';
    END IF;
END;//
DELIMITER ;

-- View All Bookings
SELECT b.Booking_ID, c.Customer_Name, e.Hall_Name, b.Event_Date, b.Booking_Status
FROM Bookings b
JOIN Customers c ON b.Customer_ID = c.Customer_ID
JOIN Event_Halls e ON b.Hall_ID = e.Hall_ID
ORDER BY b.Event_Date;
