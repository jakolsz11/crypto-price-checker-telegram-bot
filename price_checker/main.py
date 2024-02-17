from config.connectDB2 import connectDB2
from crypto_checker import Checker
import asyncio

db = connectDB2()

tokens_cursor = db.find({})
tokens = list(tokens_cursor)

checker = Checker()

async def check_all_tokens():
    for token in tokens:
        current_price = await checker.check_token(token)
        db.update_one({'_id': token['_id']}, {'$set': {'latest_price': current_price}})
        
if __name__ == '__main__':
    asyncio.run(check_all_tokens())