import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

mysql_config = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE")
}

def get_mysql_connection():
    return mysql.connector.connect(**mysql_config)
