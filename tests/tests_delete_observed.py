import pytest
from unittest.mock import AsyncMock, patch, Mock, Mock
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, ContextTypes
from bson import ObjectId
from telegram_commands.delete_observed_class import Delete_Observed, DELETE_OBSERVED, END_QUESTION

class TestDeleteObserved:
    @pytest.fixture
    def update_context_db(self):
        update = AsyncMock(spec=Update)
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        db = Mock()
        context.user_data = {}
        return update, context, db
    
    @pytest.mark.asyncio
    async def test_delete_observed_token_failure(self, update_context_db):
        update, context, db =  update_context_db
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        db.find.side_effect = Exception("Error connecting to MongoDB")
        
        delete_observed = Delete_Observed(db)
        
        result = await delete_observed.delete_observed_token(update, context)
        
        assert result == ConversationHandler.END
        
        reply_text_mock.assert_called_once_with("Sorry, something went wrong! Please try again later!")
        
    
    @pytest.mark.asyncio
    async def test_delete_observed_token_success_len_0(self, update_context_db):
        update, context, db = update_context_db
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        tokens = []
        
        db.find.return_value = tokens
        
        delete_observed = Delete_Observed(db)
        
        result = await delete_observed.delete_observed_token(update, context)
        
        assert result == ConversationHandler.END
        
        reply_text_mock.assert_called_once_with("You don't have any observed tokens")
        
    
    @pytest.mark.asyncio
    async def test_delete_observed_token_success(self, update_context_db):
        update, context, db = update_context_db
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        tokens = [
            {   
                "_id": "12345",
                "symbol": "BTCUSDT",
                "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            },
            {
                "_id": "54321",
                "symbol": "ETHUSDT",
                "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"
            }
        ]
        
        db.find.return_value = tokens
        
        delete_observed = Delete_Observed(db)
        
        result = await delete_observed.delete_observed_token(update, context)
        
        assert result == END_QUESTION
        
        keyboard = [
            [InlineKeyboardButton(token['symbol'], callback_data=str(token['_id']), switch_inline_query_current_chat="button")] for token in tokens
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        reply_text_mock.assert_called_once_with("Please choose token to delete:", reply_markup=reply_markup)
        
        
    @pytest.mark.asyncio
    async def test_delete_observed_token_callback_no(self, update_context_db):
        update, context, db = update_context_db
        
        reply_callback =AsyncMock()
        update.callback_query = reply_callback
        query = reply_callback
        
        query.data = 'no'
        
        delete_observed = Delete_Observed(db)
        
        result =  await delete_observed.delete_observed_token_callback(update, context)
        
        assert result == ConversationHandler.END
        
        query.answer.assert_called_once()
        query.message.delete.assert_called_once()
        
        
    @pytest.mark.asyncio
    async def test_delete_observed_token_callback_failure(self, update_context_db):
        update, context, db = update_context_db
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        reply_callback =AsyncMock()
        update.callback_query = reply_callback
        query = reply_callback
        
        query.data = 'yes'
        
        db.find.side_effect = Exception("Error connecting to MongoDB")
        
        delete_observed = Delete_Observed(db)
        
        result = await delete_observed.delete_observed_token_callback(update, context)
        
        assert result == ConversationHandler.END
        
        query.answer.assert_called_once()
        reply_text_mock.assert_called_once_with("Sorry, something went wrong! Please try again later!")
        
    
    @pytest.mark.asyncio
    async def test_delete_observed_token_callback_success(self, update_context_db):
        update, context, db = update_context_db
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        reply_callback =AsyncMock()
        update.callback_query = reply_callback
        query = reply_callback
        
        query.data = 'yes'
        
        tokens = [
            {   
                "_id": "12345",
                "symbol": "BTCUSDT",
                "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            },
            {
                "_id": "54321",
                "symbol": "ETHUSDT",
                "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"
            }
        ]
        
        db.find.return_value = tokens
        
        delete_observed = Delete_Observed(db)
        
        result = await delete_observed.delete_observed_token_callback(update, context)
        
        assert result == END_QUESTION
                
        keyboard = [
            [InlineKeyboardButton(token['symbol'], callback_data=str(token['_id']), switch_inline_query_current_chat="button")] for token in tokens
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.answer.assert_called_once()
        query.edit_message_text.assert_called_once_with("Please choose token to delete:", reply_markup=reply_markup)
        
    
    @pytest.mark.asyncio
    async def test_end_question_callback_failure(self, update_context_db):
        update, context, db = update_context_db
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        reply_callback =AsyncMock()
        update.callback_query = reply_callback
        query = reply_callback
        
        db.find_one.side_effect = Exception("Error connecting to MongoDB")
        
        delete_observed = Delete_Observed(db)
        
        result = await delete_observed.end_question_callback(update, context)
        
        assert result == ConversationHandler.END
        
        query.answer.assert_called_once()
        reply_text_mock.assert_called_once_with("Sorry, something went wrong! Please try again later!")
        
    
    @pytest.mark.asyncio
    async def test_end_question_callback_success_len_0(self, update_context_db):
        update, context, db = update_context_db
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        reply_callback =AsyncMock()
        update.callback_query = reply_callback
        query = reply_callback
        query.data = "65bee04c466bfd2b82aa7a12"
        
        token = {
            "_id": "65bee04c466bfd2b82aa7a12",
            "symbol": "BTCUSDT",
            "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        }
        
        db.find_one.return_value = token
        db.find.return_value = []
        
        delete_observed = Delete_Observed(db)
        
        result = await delete_observed.end_question_callback(update, context)
        
        assert result == ConversationHandler.END
        
        query.answer.assert_called_once()
        db.delete_one.assert_called_once_with({'_id': ObjectId(query.data)})
        query.edit_message_text.assert_called_once_with(f"{token['symbol']} deleted successfully from observed!")
        
        
    @pytest.mark.asyncio
    async def test_end_question_callback_success(self, update_context_db):
        update, context, db = update_context_db
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        reply_callback =AsyncMock()
        update.callback_query = reply_callback
        query = reply_callback
        query.data = "65bee04c466bfd2b82aa7a12"
        
        token = {
            "_id": "65bee04c466bfd2b82aa7a12",
            "symbol": "BTCUSDT",
            "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        }
        
        db.find_one.return_value = token
        db.find.return_value = {
            "_id": "54321",
            "symbol": "ETHUSDT",
            "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"
        }
        
        delete_observed = Delete_Observed(db)
        
        result = await delete_observed.end_question_callback(update, context)
        
        assert result == DELETE_OBSERVED
        
        keyboard = [
            [InlineKeyboardButton('YES', callback_data="yes", switch_inline_query_current_chat="button")],
            [InlineKeyboardButton('NO', callback_data="no", switch_inline_query_current_chat="button")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query.answer.assert_called_once()
        db.delete_one.assert_called_once_with({'_id': ObjectId(query.data)})
        query.edit_message_text.assert_called_once_with(f"{token['symbol']} deleted successfully from observed!")
        query.message.reply_text.assert_called_once_with("Do you want to delete another token from observed?", reply_markup=reply_markup)