# SQL Visualization API

## 📌 Overview
This is a FastAPI-based backend service that connects to a MySQL database, allowing users to:
- List all tables in the database
- Get column details of a specific table
- Retrieve data from a table (with a default limit of 10 rows)
- Insert data into a table dynamically

## 🚀 Features
✅ List all tables in the database
✅ Get table columns and their data types
✅ Retrieve data from a specific table
✅ Insert data dynamically into a table
✅ Home route to verify API status

## 🛠️ Technologies Used
- **FastAPI** (Python framework for building APIs)
- **MySQL** (Relational Database Management System)
- **Pydantic** (Data validation and serialization)
- **MySQL Connector** (For Python-MySQL connection)

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Naomi-cherono85/database_visualizer.git
cd database_visualizer
```

### 2️⃣ Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### 3️⃣ Install Dependencies
```bash
pip install fastapi uvicorn mysql-connector-python
```

### 4️⃣ Configure Environment Variables
Create a `.env` file and set up database credentials:
```ini
MYSQL_HOST=127.0.0.1
MYSQL_USER=root
MYSQL_PASSWORD=8885
MYSQL_DATABASE=my_visualization_tool
```

### 5️⃣ Run the API
```bash
uvicorn main:app --reload
```

## 🛠️ API Endpoints

### ✅ List All Tables
**GET** `/tables`
```json
{
  "tables": ["users", "orders", "products"]
}
```

### ✅ Get Table Columns
**GET** `/tables/{table_name}/columns`
```json
{
  "columns": [
    { "name": "id", "type": "INT" },
    { "name": "name", "type": "VARCHAR(255)" }
  ]
}
```

### ✅ Retrieve Data from a Table
**GET** `/tables/{table_name}/data?limit=5`
```json
{
  "data": [
    { "id": 1, "name": "Alice" },
    { "id": 2, "name": "Bob" }
  ]
}
```

### ✅ Insert Data into a Table
**POST** `/tables/{table_name}/insert`
```json
{
  "data": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```
Response:
```json
{
  "message": "Data inserted successfully"
}
```

### ✅ Home Route (API Health Check)
**GET** `/`
```json
{
  "message": "MySQL Visualization API is running!"
}
```

## 📜 License
This project is licensed under the **MIT License**.

## 🤝 Contributing
Feel free to open issues or submit PRs to improve this project!

