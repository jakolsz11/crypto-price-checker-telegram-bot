from example_data import tokens_data, observed_tokens
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
import os

MONGO_URI = os.getenv('MONGO_URI')

client = MongoClient(MONGO_URI)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as error:
    print(error)
    
db = client['crypto_telegram_bot']
collection = db['tokens']

collection.delete_many({})
collection.insert_many(tokens_data)

collection = db['observed_tokens']
collection.delete_many({})
collection.insert_many(observed_tokens)

print(collection.count_documents({}))
print(len(db.list_collection_names()))