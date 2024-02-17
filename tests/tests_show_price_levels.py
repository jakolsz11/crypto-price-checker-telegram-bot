import pytest
from unittest.mock import AsyncMock, patch, Mock, Mock
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, ContextTypes
from bson import ObjectId
from telegram_commands.show_price_levels_class import Show_Price_Levels, GET_LEVELS

class TestShowPriceLevels:
    @pytest.fixture
    def update_context_db(self):
        update = AsyncMock(spec=Update)
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        db = Mock()
        context.user_data = {}
        return update, context, db
    
    @pytest.mark.asyncio
    async def test_show_price_levels_failure(self, update_context_db):
        update, context, db = update_context_db
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        db.find.side_effect = Exception("Error connecting to MongoDB")
        
        show_price_levels = Show_Price_Levels(db)
        
        result = await show_price_levels.show_price_levels(update, context)
        
        assert result == ConversationHandler.END
        
        db.find.assert_called_once_with({})
        reply_text_mock.assert_called_once_with("Sorry, something went wrong! Please try again later!")
        
        
    @pytest.mark.asyncio
    async def test_show_price_levels_success(self, update_context_db):
        update, context, db = update_context_db
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        tokens = [
            {
                "_id": "12345",
                "symbol": "BTCUSDT",
                "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
                "latest_price": 40000,
                "reach": [41000, 39567.12, 43212.89, 38000.34, 40000]
            },
            {
                "_id": "54321",
                "symbol": "ETHUSDT",
                "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT",
                "latest_price": 40000,
                "reach": [2200, 2233.12, 2412.89]
            }
        ]
        
        db.find.return_value = tokens
        
        show_price_levels = Show_Price_Levels(db)
        
        result = await show_price_levels.show_price_levels(update, context)
        
        assert result == GET_LEVELS
        
        db.find.assert_called_once_with({})
        
        keyboard = [
            [InlineKeyboardButton(token['symbol'], callback_data=str(token['_id']), switch_inline_query_current_chat="button")] for token in tokens
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        reply_text_mock.assert_called_once_with("Please choose token: ", reply_markup=reply_markup)
        
        
    @pytest.mark.asyncio
    async def test_show_price_levels_callback_failure(self, update_context_db):
        update, context, db = update_context_db
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        reply_callback_query = AsyncMock()
        update.callback_query = reply_callback_query
        query = reply_callback_query
        query.data = '65c61cd4e9e6818adb642f12'
        
        db.find_one.side_effect = Exception("Error connecting to MongoDB")
        
        show_price_levels = Show_Price_Levels(db)
        
        result = await show_price_levels.show_price_levels_callback(update, context)
        
        assert result == ConversationHandler.END
        
        query.answer.assert_called_once()
        db.find_one.assert_called_once_with({'_id': ObjectId(query.data)})
        reply_text_mock.assert_called_once_with("Sorry, something went wrong! Please try again later!")
    
        
    @pytest.mark.asyncio
    async def test_show_price_levels_callback_success(self, update_context_db):
        update, context, db = update_context_db
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        reply_callback_query = AsyncMock()
        update.callback_query = reply_callback_query
        query = reply_callback_query
        query.data = '65c61cd4e9e6818adb642f12'
        
        token ={
            "_id": "65c61cd4e9e6818adb642f12",
            "symbol": "BTCUSDT",
            "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
            "latest_price": 40000,
            "reach": [41000, 39567.12, 43212.89, 38000.34, 40000]
        }
        
        db.find_one.return_value = token
        
        show_price_levels = Show_Price_Levels(db)
        
        result = await show_price_levels.show_price_levels_callback(update, context)
        
        assert result == ConversationHandler.END
        
        query.answer.assert_called_once()
        db.find_one.assert_called_once_with({'_id': ObjectId(query.data)})
        
        message = f"Price levels for {token['symbol']}:\n"
            
        for price in token['reach']:
            message += f"{price}\n"
        
        query.edit_message_text.assert_called_once_with(message)