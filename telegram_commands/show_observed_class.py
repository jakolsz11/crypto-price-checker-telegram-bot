from telegram import Update
from telegram.ext import ConversationHandler, ContextTypes
import requests

class Show_Observed:
    def __init__(self, db):
        self.db = db
        
    async def show_observed(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            tokens_cursor = self.db.find({})
        except:
            print("Something went wrong while downloading data to show observed")
            await update.message.reply_text("Sorry, something went wrong! Please try again later!")
            return ConversationHandler.END
        else:
            tokens = list(tokens_cursor)
            
            if len(tokens) == 0:
                await update.message.reply_text("You don't have any observed tokens")
            else:
                message = ""
                    
                for token in tokens:
                    try:
                        response = requests.get(token['api_url'])
                        response.raise_for_status()
                    except:
                        text = f"{token['symbol']} - can't get data\n"
                    else:
                        data = response.json()
                        text = f"{token['symbol']} - {data['price']}\n"
                    finally:
                        message += text
                    
                await update.message.reply_text(f"{message}")
                
            return ConversationHandler.END