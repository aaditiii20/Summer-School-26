#DEMO
from pymongo import MongoClient

def connect_to_mongo():
    try:
        client = MongoClient("mongodb://localhost:27017")  # or your MongoDB Atlas URI
        db = client["aryavartta_db"]  # your database name
        print(" MongoDB connected successfully")
        return db
    except Exception as e:
        print(f" MongoDB connection failed: {e}")
        return None
