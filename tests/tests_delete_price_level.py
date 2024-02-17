import pytest
from unittest.mock import AsyncMock, Mock
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, ContextTypes
from bson import ObjectId
from telegram_commands.delete_price_level_class import Delete_Price_Level, CHOOSE_SYMBOL, DELETE_COMMAND, END_QUESTION

class TestDeletePriceLevel:
    @pytest.fixture
    def update_context_db(self):
        update = AsyncMock(spec=Update)
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        db = Mock()
        context.user_data = {}
        return update, context, db

    @pytest.mark.asyncio
    async def test_delete_price_level_failure(self, update_context_db):
        update, context, db = update_context_db
        
        db.find.side_effect = Exception("Error connecting to MongoDB")
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        delete_price_level = Delete_Price_Level(db)
        
        result = await delete_price_level.delete_price_level(update, context)
        
        assert result == ConversationHandler.END
        
        reply_text_mock.assert_called_once_with("Sorry, something went wrong! Please try again later!")
        
        
    @pytest.mark.asyncio
    async def test_delete_price_level_success(self, update_context_db):
        update, context, db = update_context_db
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
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        keyboard = [
            [InlineKeyboardButton(token['symbol'], callback_data=str(token['_id']), switch_inline_query_current_chat="button")] for token in tokens
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        delete_price_level = Delete_Price_Level(db)
        
        result = await delete_price_level.delete_price_level(update, context)
        
        assert result == CHOOSE_SYMBOL
        
        reply_text_mock.assert_called_once_with("Please choose token: ", reply_markup=reply_markup)
        
    
    @pytest.mark.asyncio
    async def test_choose_level_callback_no(self, update_context_db):
        update, context, db = update_context_db
        
        reply_callback_query = AsyncMock()
        update.callback_query = reply_callback_query
        query = reply_callback_query
        query.data = 'no'
        
        delete_price_level = Delete_Price_Level(db)
        
        result = await delete_price_level.choose_level_callback(update, context)
        
        assert result == ConversationHandler.END
        
        query.answer.assert_called_once()
        query.message.delete.assert_called_once()
        
        
    @pytest.mark.asyncio
    async def test_choose_level_callback_failure(self, update_context_db):
        update, context, db = update_context_db
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        reply_callback_query = AsyncMock()
        update.callback_query = reply_callback_query
        
        query = reply_callback_query
        query.data = '65bee04c466bfd2b82aa7a12'
                
        db.find_one.side_effect = Exception("Error connecting to MongoDB")
        
        delete_price_level = Delete_Price_Level(db)
        
        result = await delete_price_level.choose_level_callback(update, context)
        
        assert result == ConversationHandler.END
        assert context.user_data['token_id'] == query.data
        
        reply_text_mock.assert_called_once_with("Sorry, something went wrong! Please try again later!")
        
        
    @pytest.mark.asyncio
    async def test_choose_level_callback_success(self, update_context_db):
        update, context, db = update_context_db
        
        reply_callback_query = AsyncMock()
        update.callback_query = reply_callback_query
        query = reply_callback_query
        
        query.data = '65bee04c466bfd2b82aa7a12'
        
        token = {
            "_id": query.data,
            "symbol": "BTCUSDT",
            "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
            "latest_price": 40000,
            "reach": [41000, 39567.12, 43212.89, 38000.34, 40000]
        }
        
        db.find_one.return_value = token        
        
        delete_price_level = Delete_Price_Level(db)
        
        result = await delete_price_level.choose_level_callback(update, context)
        
        
        assert result == DELETE_COMMAND
        assert context.user_data['token_id'] == query.data
        
        keyboard = [
            [InlineKeyboardButton(price, callback_data=index, switch_inline_query_current_chat="button")] for index, price in enumerate(token['reach'])
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        db.find_one.assert_called_once_with({'_id': ObjectId(query.data)})
        query.edit_message_text.assert_called_once_with(f"{token['symbol']}\nPlease choose price level to delete: ", reply_markup=reply_markup)
        
    @pytest.mark.asyncio
    async def test_delete_price_level_callback_failure(self, update_context_db):
        update, context, db = update_context_db
        
        context.user_data['token_id'] = '65bee04c466bfd2b82aa7a12'
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        reply_callback_query = AsyncMock()
        update.callback_query = reply_callback_query
        query = reply_callback_query
        
        db.find_one.side_effect = Exception("Error connecting to MongoDB")
        
        delete_price_level = Delete_Price_Level(db)
        
        result = await delete_price_level.delete_price_level_callback(update, context)
        assert result == ConversationHandler.END
        
        reply_text_mock.assert_called_once_with("Sorry, something went wrong! Please try again later!")
        query.answer.assert_called_once()
        
        
    @pytest.mark.asyncio
    async def test_delete_price_level_callback_success_len_0(self, update_context_db):
        update, context, db = update_context_db
        
        context.user_data['token_id'] = '65bee04c466bfd2b82aa7a12'
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        reply_callback_query = AsyncMock()
        update.callback_query = reply_callback_query
        query = reply_callback_query
        query.data = 0
        deleted_price_level = 40000
        
        token = {
            "_id": context.user_data['token_id'],
            "symbol": "BTCUSDT",
            "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
            "latest_price": 40000,
            "reach": [deleted_price_level]
        }
        
        db.find_one.return_value = token
        
        delete_price_level = Delete_Price_Level(db)
        
        result = await delete_price_level.delete_price_level_callback(update, context)
        assert result == ConversationHandler.END
        
        query.answer.assert_called_once()
        
        db.delete_one.assert_called_once_with({'_id': token['_id']})
        query.edit_message_text.assert_called_once_with(f"{token['symbol']} - {deleted_price_level} deleted successfully")
        
        
    @pytest.mark.asyncio
    async def test_delete_price_level_callback_success(self, update_context_db):
        update, context, db = update_context_db
        
        context.user_data['token_id'] = '65bee04c466bfd2b82aa7a12'
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        reply_callback_query = AsyncMock()
        update.callback_query = reply_callback_query
        query = reply_callback_query
        query.data = 2
        deleted_price_level = 40000
        
        token = {
            "_id": context.user_data['token_id'],
            "symbol": "BTCUSDT",
            "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
            "latest_price": 40000,
            "reach": [39000, 39500, deleted_price_level, 43000]
        }
        
        db.find_one.return_value = token
        
        delete_price_level = Delete_Price_Level(db)
        
        result = await delete_price_level.delete_price_level_callback(update, context)
        assert result == CHOOSE_SYMBOL
        
        query.answer.assert_called_once()
        
        db.update_one.assert_called_once_with({'_id': token['_id']}, {'$set': {'reach': token['reach']}})
        query.edit_message_text.assert_called_once_with(f"{token['symbol']} - {deleted_price_level} deleted successfully")
        
        keyboard = [
            [InlineKeyboardButton('YES', callback_data=f"{token['_id']}", switch_inline_query_current_chat="button")],
            [InlineKeyboardButton('NO', callback_data="no", switch_inline_query_current_chat="button")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.message.reply_text.assert_called_once_with(f"Do you want to delete another price level for {token['symbol']}: ", reply_markup=reply_markup)