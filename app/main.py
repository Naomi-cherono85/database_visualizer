from fastapi import FastAPI, HTTPException, Depends
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from .auth import router as auth_router
from .routes import mysql_routes as mysql_router
from .utils import get_db_connection
from .auth.Oauth2 import get_current_user
from .auth.schema import UserInDB
from .models import create_tables  

app = FastAPI()

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

app.include_router(auth_router.router)
app.include_router(mysql_router.router)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Protected routes
@app.get("/tables")
def list_tables(current_user: UserInDB = Depends(get_current_user)):
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

@app.get("/tables/{table_name}/columns")
def get_table_columns(table_name: str, current_user: UserInDB = Depends(get_current_user)):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]

        if table_name not in tables:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found.")

        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = [{"name": row[0], "type": row[1]} for row in cursor.fetchall()]
        return {"columns": columns}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching columns: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@app.get("/tables/{table_name}/data")
def get_table_data(
    table_name: str, 
    current_user: UserInDB = Depends(get_current_user), 
    limit: int = 10
):
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

class InsertData(BaseModel):
    data: Dict[str, str]

@app.post("/tables/{table_name}/insert")
def insert_data(
    table_name: str,  
    insert_data: InsertData, 
    current_user: UserInDB = Depends(get_current_user)
):
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
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Error inserting data: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@app.get("/")
def health_check():
    return {"message": "MySQL Visualization API is running!"}