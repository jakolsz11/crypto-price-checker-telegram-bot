# Crypto Price Checker Telegram Bot

## Introduction
This is a Telegram Bot that allows users to track prices of selected cryptocurrencies and receive notifications when the price of a cryptocurrency exceeds a previously set level.
Users have full freedom in setting price levels; they can add, remove, and view the levels they are already observing. Additionally, they have the ability to monitor selected cryptocurrencies, meaning that upon entering a Telegram command, the bot sends a message with the observed cryptocurrencies and their current price.
The data is retrieved from the BINANCE API. The application stores data in MongoDB.

## Installation
First you have to install requirements.txt:
```
pip install -r requirements.tx
```
If you get an error: 'Defaulting to user installation because normal site-packages is not writeable' use this:
``` 
python3 -m pip install -r requirements.txt
```
Next you have to create .env file in the main directory and paste this inside:
```
MONGO_URI="**********************************************************************"
BOT_TOKEN="*******************************"
CHAT_ID="***************"
```
Now you have to create new telegram bot. Here is [telegram documentation](https://core.telegram.org/bots/features#botfather). <br>
To get chat_id I recommend to use [@raw_info_bot](https://t.me/raw_info_bot), start conversation with this bot using /start command and then you see your chat_id.<br>
Next, replace **** in the .env file for BOT_TOKEN and CHAT_ID. <br>
IMPORTANT!! YOU CANNOT CHANGE THE VARIABLE NAMES! <br>

Next, you have to create account on [MongoDB](https://www.mongodb.com/). From there you get MONGO_URI, which you have to paste to .env file. <br>
Here is [MongoDB documentation](https://www.mongodb.com/docs/).

### Check is working
Run this:
```
cd tests
python3 -m pytest tests.py
```
If all tests passed, the code was install correctly!

Now you can run this code.

First you have to upload data to MongoDb:
```
cd ..
cd seeder
python3 reset_data.py
```
And then you can run telegram bot:
```
cd ..
cd telegram_commands
python3 telegram_commands.py
```

Now you can corespond with your telegram bot.


### Price Checker
You can also run price checker, but you have to upload it on a server eg. Google Cloud and set crontab and tmux to run this code eg. every minute. Because on pc when you run this, it only runs once.

To run this:
```
cd ..
cd price_checker
python3 main.py
```

## Telegram Commands
Send '/setcommands' to BotFather, then choose your bot and the last part is to paste this:
```
addpricelevel - Add new price level
deletepricelevel - Delete price level
showpricelevels - Show all price levels
addtoobserved - Add new token to observed
deletefromobserved - Delete token from observed
showobserved - Show all observed tokens
cancel - Cancel current action
```
| Command  | Description |
| ------------- | ------------- |
| /addpricelevel  | Add new price level  |
| /deletepricelevel  | Delete price level  |
| /showpricelevels  | Show all price levels  |
| /addtoobserved  | Add new token to observed  |
| /deletefromobserved  | Delete token from observed  |
| /showobserved  | Show all observed tokens  |
| /cancel  | Cancel current action  |
