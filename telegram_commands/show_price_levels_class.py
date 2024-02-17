from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, ContextTypes
from bson import ObjectId

GET_LEVELS = 6

class Show_Price_Levels:
    def __init__(self, db):
        self.db = db
        
    async def show_price_levels(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            tokens_cursor = self.db.find({})
        except:
            print("Unable to connect to MongoDB while showing price level")
            await update.message.reply_text("Sorry, something went wrong! Please try again later!")
            return ConversationHandler.END
        else:
            tokens = list(tokens_cursor)
            
            keyboard = [
                [InlineKeyboardButton(token['symbol'], callback_data=str(token['_id']), switch_inline_query_current_chat="button")] for token in tokens
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text("Please choose token: ", reply_markup=reply_markup)
            return GET_LEVELS
        

    async def show_price_levels_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        try:
            token = self.db.find_one({'_id': ObjectId(query.data)})
        except:
            print("Something went wrong while finding token")
            await update.message.reply_text("Sorry, something went wrong! Please try again later!")
            return ConversationHandler.END
        else:
            message = f"Price levels for {token['symbol']}:\n"
            
            for price in token['reach']:
                message += f"{price}\n"
                
            await query.edit_message_text(message)
            return ConversationHandler.END