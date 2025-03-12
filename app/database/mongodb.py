from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGODB_URI"))
mongo_db = mongo_client[os.getenv("MONGODB_DATABASE")]
