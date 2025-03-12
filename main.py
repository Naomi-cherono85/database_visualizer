from fastapi import FastAPI, HTTPException
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to establish database connection
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "8885"),
            database=os.getenv("MYSQL_DATABASE", "my_visualization_tool")
        )
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


# ✅ 1️⃣ List all tables in the database
@app.get("/tables")
def list_tables():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        return {"tables": tables}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tables: {str(e)}")
    finally:
        cursor.close()
        connection.close()


# ✅ 2️⃣ Get table columns and their data types
@app.get("/tables/{table_name}/columns")
def get_table_columns(table_name: str):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Validate if table exists
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]

        if table_name not in tables:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found.")

        # Use backticks to avoid syntax errors
        query = f"DESCRIBE `{table_name}`"
        cursor.execute(query)
        columns = [{"name": row[0], "type": row[1]} for row in cursor.fetchall()]
        return {"columns": columns}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching columns: {str(e)}")

    finally:
        cursor.close()
        connection.close()



# ✅ 3️⃣ Get data from a specific table (default limit: 10)
@app.get("/tables/{table_name}/data")
def get_table_data(table_name: str, limit: int = 10):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT %s", (limit,))
        data = cursor.fetchall()
        return {"data": data}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    finally:
        cursor.close()
        connection.close()


# ✅ 4️⃣ Insert data into a table dynamically
class InsertData(BaseModel):
    data: Dict[str, str]  # Dictionary of column names and values

@app.post("/tables/{table_name}/insert")
def insert_data(table_name: str, insert_data: InsertData):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        columns = ", ".join(insert_data.data.keys())
        values = ", ".join(["%s"] * len(insert_data.data))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

        cursor.execute(sql, tuple(insert_data.data.values()))
        connection.commit()

        return {"message": "Data inserted successfully"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error inserting data: {str(e)}")
    finally:
        cursor.close()
        connection.close()


# ✅ 5️⃣ Home route to check if the API is running
@app.get("/")
def home():
    return {"message": "MySQL Visualization API is running!"}
