from telegram_bot import TelegramBot
import requests

API_URL = "https://api.binance.com/api/v3/ticker/price?symbol="

class Checker:
    def __init__(self):
        self.bot = TelegramBot()
        
    async def check_token(self, token):
        try:
            response = requests.get(token['api_url'])
            response.raise_for_status()
            data = response.json()
            current_price = data['price']
            await self.is_reach_level(token['latest_price'], current_price, token['reach'], token)
            return current_price
        except requests.exceptions.RequestException as e:
            print(f'Błąd podczas pobierania ceny: {e}')
            return
          
        
    async def is_reach_level(self, latest_price, current_price, reach, token):
        for price in reach:
            if float(price) - float(latest_price) >= 0 and float(current_price) > float(price):
                await self.bot.send_telegram_message(f"{token['symbol']} is above {price}!\nCurrent price is {current_price}")
            elif float(price) - float(latest_price) <= 0 and float(current_price) < float(price):
                await self.bot.send_telegram_message(f"{token['symbol']} is below {price}!\nCurrent price is {current_price}")
            else:
                continue
        
        return
        
    