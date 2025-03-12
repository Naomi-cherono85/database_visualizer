from fastapi import APIRouter, Depends
from ..database.mysql_db import get_mysql_connection
from ..auth.schema import UserInDB
from ..auth.Oauth2 import get_current_user

router = APIRouter()

@router.get("/tables")
def list_tables(current_user: UserInDB = Depends(get_current_user)):
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()
        conn.close()
        return {"tables": tables}
    except Exception as e:
        return {"error": str(e)}

@router.get("/table/{table_name}")
def get_table_data(table_name: str, current_user: UserInDB = Depends(get_current_user)):
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"table": table_name, "data": rows}
    except Exception as e:
        return {"error": str(e)}
