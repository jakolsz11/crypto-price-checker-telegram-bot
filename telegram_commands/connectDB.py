from pymongo import MongoClient

def connectDB(collection_name):
    MONGO_URI = 'mongodb+srv://olszanecki11:OrCTzBIeISvd6mfu@cluster0.lfqxmh9.mongodb.net/?retryWrites=true&w=majority'
    
    client = MongoClient(MONGO_URI)
    
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as error:
        print(error)
        
    db = client['crypto_telegram_bot']
    collection = db[collection_name]
    
    return collection