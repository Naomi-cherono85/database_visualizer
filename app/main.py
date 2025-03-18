from fastapi import FastAPI, HTTPException, Form, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from pymysql import MySQLError, connect, cursors
from typing import Optional, Dict, List
import os
import uuid
import csv
import json
import io

app = FastAPI(title="MySQL Visualizer PRO", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection Manager
class MySQLConnectionManager:
    def __init__(self):
        self.connections = {}

    def create_connection(self, config: Dict) -> str:
        connection_id = str(uuid.uuid4())
        try:
            conn = connect(
                host=config['host'],
                user=config['username'],
                password=config['password'],
                database=config['database'],
                port=config['port'],
                cursorclass=cursors.DictCursor
            )
            self.connections[connection_id] = conn
            return connection_id
        except MySQLError as e:
            raise HTTPException(status_code=400, detail=f"MySQL Error: {e}")

    def get_connection(self, connection_id: str):
        return self.connections.get(connection_id)

mysql_manager = MySQLConnectionManager()

@app.post("/connect")
async def connect_mysql(
    host: str = Form(...),
    database: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    port: int = Form(3306)
):
    """Establish MySQL connection"""
    try:
        conn_id = mysql_manager.create_connection({
            'host': host,
            'database': database,
            'username': username,
            'password': password,
            'port': port
        })
        return {"connection_id": conn_id, "database": database}
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

@app.get("/tables")
async def list_tables(connection_id: str):
    """List all tables in database"""
    conn = mysql_manager.get_connection(connection_id)
    if not conn:
        raise HTTPException(400, "Invalid connection")
    
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = [list(table.values())[0] for table in cursor.fetchall()]
    return tables

@app.get("/table/{table_name}")
async def get_table_data(
    table_name: str,
    connection_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100)
):
    """Get paginated table data"""
    conn = mysql_manager.get_connection(connection_id)
    if not conn:
        raise HTTPException(400, "Invalid connection")

    offset = (page - 1) * per_page
    try:
        with conn.cursor() as cursor:
            # Get total rows
            cursor.execute(f"SELECT COUNT(*) AS total FROM {table_name}")
            total = cursor.fetchone()['total']
            
            # Get data
            cursor.execute(f"""
                SELECT * FROM {table_name}
                LIMIT {per_page} OFFSET {offset}
            """)
            data = cursor.fetchall()
            
            # Get columns
            cursor.execute(f"DESCRIBE {table_name}")
            columns = [col['Field'] for col in cursor.fetchall()]
            
        return {
            "table": table_name,
            "columns": columns,
            "data": data,
            "total": total,
            "page": page
        }
    except MySQLError as e:
        raise HTTPException(400, f"MySQL Error: {e}")

@app.get("/schema/{table_name}")
async def get_table_schema(table_name: str, connection_id: str):
    """Get table relationships"""
    conn = mysql_manager.get_connection(connection_id)
    if not conn:
        raise HTTPException(400, "Invalid connection")

    try:
        with conn.cursor() as cursor:
            # Get foreign keys
            cursor.execute(f"""
                SELECT 
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_NAME = '{table_name}'
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            relationships = cursor.fetchall()
            
            # Get columns
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
        return {
            "table": table_name,
            "columns": columns,
            "relationships": relationships
        }
    except MySQLError as e:
        raise HTTPException(400, f"MySQL Error: {e}")

@app.get("/export/{table_name}")
async def export_table(
    table_name: str,
    connection_id: str,
    format: str = Query(..., regex="^(csv|json|sql)$")
):
    """Export table data"""
    conn = mysql_manager.get_connection(connection_id)
    if not conn:
        raise HTTPException(400, "Invalid connection")

    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            cursor.execute(f"DESCRIBE {table_name}")
            columns = [col['Field'] for col in cursor.fetchall()]
            
        if format == 'csv':
            return export_csv(data, columns, table_name)
        elif format == 'json':
            return export_json(data, table_name)
        elif format == 'sql':
            return export_sql(data, table_name, columns)
            
    except MySQLError as e:
        raise HTTPException(400, f"MySQL Error: {e}")

def export_csv(data, columns, table_name):
    csv_data = io.StringIO()
    writer = csv.DictWriter(csv_data, fieldnames=columns)
    writer.writeheader()
    writer.writerows(data)
    return Response(
        content=csv_data.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={table_name}.csv"}
    )

def export_json(data, table_name):
    return Response(
        content=json.dumps(data, default=str),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={table_name}.json"}
    )

def export_sql(data, table_name, columns):
    sql = [f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES"]
    for row in data:
        values = [f"'{str(v)}'" if not isinstance(v, (int, float)) else str(v) for v in row.values()]
        sql.append(f"({', '.join(values)}),")
    sql[-1] = sql[-1].rstrip(',') + ';'
    return Response(
        content="\n".join(sql),
        media_type="text/sql",
        headers={"Content-Disposition": f"attachment; filename={table_name}.sql"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)