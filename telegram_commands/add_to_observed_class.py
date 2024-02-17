from telegram import Update
from telegram.ext import ConversationHandler, ContextTypes
import requests

API_URL = "https://api.binance.com/api/v3/ticker/price?symbol="
GET_TOKEN_OBSERVED = 7


class Add_To_Observed:
    def __init__(self, db):
        self.db = db

    async def start_add_to_observed(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Enter the token symbol!")
        return GET_TOKEN_OBSERVED


    async def add_to_observed(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        token_symbol = update.message.text.upper().strip()
        
        try:
            response = requests.get(f"{API_URL}{token_symbol}")
            response.raise_for_status()
        except:
            await update.message.reply_text(f"{token_symbol} is unavailable.")
        else:
            
            data = response.json()
            current_price = data['price']
            
            if self.db.find_one({'symbol': token_symbol}):
                await update.message.reply_text(f"{token_symbol} is already observed!\nCurrent price is {current_price}")
            else:
                newToken = {
                    "symbol": token_symbol,
                    "api_url": f"{API_URL}{token_symbol}"
                }
                
                self.db.insert_one(newToken)
                await update.message.reply_text(f"{token_symbol} successfully added to observed!\nCurrent price is {current_price}")
        finally:
            return ConversationHandler.END
    
    