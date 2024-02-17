from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, ContextTypes
import requests

CRYPTO_SYMBOL, PRICE_LEVEL, DELETE_COMMAND = 1, 2, 3
API_URL = "https://api.binance.com/api/v3/ticker/price?symbol="

class Add_Price_Level:
    def __init__(self, db):
        self.db = db
        
    async def start_adding(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Enter the symbol e.g. BTCUSDT")
        return CRYPTO_SYMBOL
    
    async def get_crypto_symbol(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        crypto_symbol = update.message.text.upper().strip()
        context.user_data['crypto_symbol'] = crypto_symbol
        
        try:
            response = requests.get(f"{API_URL}{crypto_symbol}")
            response.raise_for_status()
        except:
            await update.message.reply_text(f"{crypto_symbol} is unavailable.")
            context.user_data.clear()
            return ConversationHandler.END
        else:
            data = response.json()
            current_price = data['price']
            context.user_data['current_price'] = current_price
            await update.message.reply_text(f"{crypto_symbol}\nCurrent price: {current_price}")
            await update.message.reply_text(f"Specify the price level to observation for {crypto_symbol}")
            return PRICE_LEVEL    
        
    async def get_price_level(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        price_level = update.message.text.replace(" ", "").replace(",", ".").strip()    
        tokenExists = self.db.find_one({"symbol": context.user_data['crypto_symbol']})
        
        if tokenExists:
            if float(price_level) not in tokenExists['reach']:
                tokenExists['reach'].append(float(price_level))
                tokenExists['reach'].sort()
                self.db.update_one({'_id': tokenExists['_id']}, {'$set': tokenExists})         
                await update.message.reply_text(f'Price level added successfully!\n{context.user_data['crypto_symbol']}\n{price_level}')
                return ConversationHandler.END
            else:
                keyboard = [
                    [InlineKeyboardButton('Add another', callback_data='another', switch_inline_query_current_chat="button")],
                    [InlineKeyboardButton('Cancel', callback_data='cancel', switch_inline_query_current_chat="button")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(f'Price level is already added!', reply_markup=reply_markup)
        else:
            newToken = {
                "symbol": context.user_data['crypto_symbol'],
                "api_url": f"https://api.binance.com/api/v3/ticker/price?symbol={context.user_data['crypto_symbol']}",
                "latest_price": float(context.user_data['current_price']),
                "reach": [float(price_level)]
            }

            try:
                self.db.insert_one(newToken)
            except:
                print("Something went wrong while adding token")
                await update.message.reply_text("Sorry, something went wrong! Please try again later!")
            else:
                await update.message.reply_text(f'Price level added successfully!\n{context.user_data['crypto_symbol']}\n{price_level}')     
                
            return ConversationHandler.END
        
        
    async def cancel_adding(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Operation canceled.")
        context.user_data.clear()
        return ConversationHandler.END


    async def add_price_level_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        if query.data == 'another':
            await query.edit_message_text(f"Specify the price level to observation for {context.user_data['crypto_symbol']}")
            return PRICE_LEVEL
        elif query.data == 'cancel':
            await query.edit_message_text("Operation canceled.")
            context.user_data.clear()
            return ConversationHandler.END