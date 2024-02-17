from telegram import Bot
from dotenv import load_dotenv
load_dotenv()
import os

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

class TelegramBot(Bot):
    def __init__(self):
        super().__init__(token=BOT_TOKEN)
        
    async def send_telegram_message(self, message_text):
        await self.send_message(chat_id=CHAT_ID, text=message_text)