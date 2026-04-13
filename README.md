# MinRide – Driver-Customer Matching System

## Description
MinRide is a Python-based application that simulates a ride-hailing system.  
The system allows managing drivers, customers, and trips, and matches customers with the nearest available driver.

This project focuses on implementing core logic and algorithms for distance calculation and matching rather than real-world map integration.

---

## Features
- Manage drivers and customers
- Create and manage ride requests
- Match customers with the nearest driver
- Calculate trip distance using a simplified "straight-line" (Euclidean) approach
- Basic graphical user interface using Tkinter

---

## Technologies
- Python 3
- Tkinter (GUI)
- CSV (data storage)
- Data Structures & Algorithms (distance calculation, matching logic)

---

## System Structure
- `App_Main.py`: Main entry point of the application
- `services/`: Business logic (driver, customer, trip handling)
- `data/`: Input data (drivers, customers, trips)
- `main_pages/`: UI screens
- `TinhNang.py`: Feature handling logic

---

## How It Works
The system calculates the distance between drivers and customers using a simplified mathematical formula (Euclidean distance).  
Based on this, it selects the closest available driver for a given customer request.

---

## Requirements
- Python 3.9 or higher
- Required libraries:
  - tkinter
  - PIL
  - os, csv, copy, pathlib, math, random (built-in)

---

## Demo
<img width="552" height="1007" alt="Demo_MinRide" src="https://github.com/user-attachments/assets/abd2b9b0-cd06-4654-9ec7-5982eaace262" />

---

## How to Run

### Step 1: Open terminal in project folder

### Step 2: Run the application
```bash
python App_Main.py

