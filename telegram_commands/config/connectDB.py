from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
import os

def connectDB(collection_name):
    MONGO_URI = os.getenv("MONGO_URI")
    client = MongoClient(MONGO_URI)
    
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as error:
        print(error)
        
    db = client['crypto_telegram_bot']
    collection = db[collection_name]
    
    return collection