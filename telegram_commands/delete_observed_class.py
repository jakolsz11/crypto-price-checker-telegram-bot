from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, ContextTypes
from bson import ObjectId

DELETE_OBSERVED, END_QUESTION = 8, 9

class Delete_Observed:
    def __init__(self, db):
        self.db = db
        
    async def delete_observed_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
        try:
            tokens_cursor = self.db.find({})
        except:
            print("Something went wrong while downloading data for delete observed")
            await update.message.reply_text("Sorry, something went wrong! Please try again later!")
            return ConversationHandler.END
        else:
            tokens = list(tokens_cursor)
            
            if len(tokens) == 0:
                await update.message.reply_text("You don't have any observed tokens")
                return ConversationHandler.END
            else:
                keyboard = [
                    [InlineKeyboardButton(token['symbol'], callback_data=str(token['_id']), switch_inline_query_current_chat="button")] for token in tokens
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text("Please choose token to delete:", reply_markup=reply_markup)
                return END_QUESTION
            
        
        
    async def delete_observed_token_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
            
        
        if query.data == 'no':
            await query.message.delete()
            return ConversationHandler.END
        else:
            try:
                tokens_cursor = self.db.find({})
            except:
                print("Something went wrong while downloading data for delete observed")
                await update.message.reply_text("Sorry, something went wrong! Please try again later!")
                return ConversationHandler.END
            else:
                tokens = list(tokens_cursor)
                
                keyboard = [
                    [InlineKeyboardButton(token['symbol'], callback_data=str(token['_id']), switch_inline_query_current_chat="button")] for token in tokens
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text("Please choose token to delete:", reply_markup=reply_markup)
                return END_QUESTION


    async def end_question_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query        
        await query.answer()
        
        try:
            token = self.db.find_one({'_id': ObjectId(query.data)})
        except:
            print("Something went wrong while deleting observed token")
            await update.message.reply_text("Sorry, something went wrong! Please try again later!")
            return ConversationHandler.END
        else:
            self.db.delete_one({'_id': ObjectId(query.data)})
            await query.edit_message_text(f"{token['symbol']} deleted successfully from observed!")
            
            data = list(self.db.find({}))
            
            if len(data) == 0:
                return ConversationHandler.END
            else:        
                keyboard = [
                    [InlineKeyboardButton('YES', callback_data="yes", switch_inline_query_current_chat="button")],
                    [InlineKeyboardButton('NO', callback_data="no", switch_inline_query_current_chat="button")]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.reply_text("Do you want to delete another token from observed?", reply_markup=reply_markup)
                return DELETE_OBSERVED