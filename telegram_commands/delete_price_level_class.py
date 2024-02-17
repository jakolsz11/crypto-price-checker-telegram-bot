from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, ContextTypes
from bson import ObjectId

CHOOSE_SYMBOL, DELETE_COMMAND, END_QUESTION = 3, 4, 5

class Delete_Price_Level:
    def __init__(self, db):
        self.db = db
        
    async def delete_price_level(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
        try:
            tokens_cursor = self.db.find({})
        except:
            print("Unable to connect to MongoDB while delete price level")
            await update.message.reply_text("Sorry, something went wrong! Please try again later!")
            return ConversationHandler.END
        else:
            tokens = list(tokens_cursor)
            
            keyboard = [
                [InlineKeyboardButton(token['symbol'], callback_data=str(token['_id']), switch_inline_query_current_chat="button")] for token in tokens
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text("Please choose token: ", reply_markup=reply_markup)
            return CHOOSE_SYMBOL
        
        
    async def choose_level_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
        query = update.callback_query
        await query.answer()
        
        if query.data == 'no':
            await query.message.delete()
            return ConversationHandler.END
        else:
            context.user_data['token_id'] = query.data
            
            try:
                token = self.db.find_one({'_id': ObjectId(query.data)})
            except:
                print("Something went wrong while finding token")
                await update.message.reply_text("Sorry, something went wrong! Please try again later!")
                return ConversationHandler.END
            else:
                keyboard = [
                    [InlineKeyboardButton(price, callback_data=index, switch_inline_query_current_chat="button")] for index, price in enumerate(token['reach'])
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(f"{token['symbol']}\nPlease choose price level to delete: ", reply_markup=reply_markup)
                return DELETE_COMMAND
            
    
    async def delete_price_level_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        
        await query.answer()
        
        try:
            token = self.db.find_one({'_id': ObjectId(context.user_data['token_id'])})
        except:
            print("Something went wrong while deleting price level")
            await update.message.reply_text("Sorry, something went wrong! Please try again later!")
            return ConversationHandler.END
        else:
            
            delete_price_level = token['reach'][int(query.data)]
            token['reach'].pop(int(query.data))
            
            if len(token['reach']) == 0:
                self.db.delete_one({'_id': token['_id']})
                await query.edit_message_text(f"{token['symbol']} - {delete_price_level} deleted successfully")
                return ConversationHandler.END
            else:
                self.db.update_one({'_id': token['_id']}, {'$set': {'reach': token['reach']}})
                await query.edit_message_text(f"{token['symbol']} - {delete_price_level} deleted successfully")
                
                keyboard = [
                    [InlineKeyboardButton('YES', callback_data=f"{token['_id']}", switch_inline_query_current_chat="button")],
                    [InlineKeyboardButton('NO', callback_data="no", switch_inline_query_current_chat="button")]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.reply_text(f"Do you want to delete another price level for {token['symbol']}: ", reply_markup=reply_markup)
                return CHOOSE_SYMBOL