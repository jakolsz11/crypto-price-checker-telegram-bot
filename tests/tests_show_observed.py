import pytest
from unittest.mock import AsyncMock, patch, Mock, Mock
from telegram import Update
from telegram.ext import ConversationHandler, ContextTypes
import requests
from telegram_commands.show_observed_class import Show_Observed

class TestShowObserved:
    @pytest.fixture
    def update_context_db(self):
        update = AsyncMock(spec=Update)
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        db = Mock()
        context.user_data = {}
        return update, context, db
    
    
    @pytest.mark.asyncio
    async def test_show_observed_failure_find(self, update_context_db):
        update, context, db = update_context_db
        
        reply_mock_text = AsyncMock()
        update.message.reply_text = reply_mock_text
        
        db.find.side_effect = Exception("Error connecting to MongoDB")
        
        show_observed = Show_Observed(db)
        
        result = await show_observed.show_observed(update, context)
        
        assert result == ConversationHandler.END
        
        reply_mock_text.assert_called_once_with("Sorry, something went wrong! Please try again later!")
        
        
    @pytest.mark.asyncio
    async def test_show_observed_success_len_0(self, update_context_db):
        update, context, db = update_context_db
        
        reply_mock_text = AsyncMock()
        update.message.reply_text = reply_mock_text
        
        tokens = []
        
        db.find.return_value = tokens
        
        show_observed = Show_Observed(db)
        
        result = await show_observed.show_observed(update, context)
        
        assert result == ConversationHandler.END
        
        reply_mock_text.assert_called_once_with("You don't have any observed tokens")
        
        
    @pytest.mark.asyncio
    @patch('requests.get', side_effect=requests.RequestException)
    async def test_show_observed_failure_requests(self, mock_get, update_context_db):
        update, context, db = update_context_db
        
        reply_mock_text = AsyncMock()
        update.message.reply_text = reply_mock_text
        
        tokens = [
            {
                "_id": "65c614e953664e7effd3835c",
                "symbol": "JUPUSDT",
                "api_url": "https://api.binance.com/api/v3/ticker/pric?symbol=JUPUSDT"
            },
            {
                "_id": "65c61cd4e9e6818adb642f0f",
                "symbol": "ETHUSDT",
                "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"
            }
        ]        
        
        db.find.return_value = tokens
        
        show_observed = Show_Observed(db)
        
        result = await show_observed.show_observed(update, context)
        
        assert result == ConversationHandler.END
        
        message = ""
        for token in tokens:
            message += f"{token['symbol']} - can't get data\n"
        
        reply_mock_text.assert_called_once_with(f"{message}")
        
        
    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_show_observed_success(self, mock_get, update_context_db):
        update, context, db = update_context_db
        
        reply_mock_text = AsyncMock()
        update.message.reply_text = reply_mock_text
        
        tokens = [
            {
                "_id": "65c614e953664e7effd3835c",
                "symbol": "JUPUSDT",
                "api_url": "https://api.binance.com/api/v3/ticker/pric?symbol=JUPUSDT"
            },
            {
                "_id": "65c61cd4e9e6818adb642f0f",
                "symbol": "ETHUSDT",
                "api_url": "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"
            }
        ]        
        
        db.find.return_value = tokens
        
        current_price = 45000
        
        mock_response = Mock()
        mock_response.json.return_value = {'price': current_price}
        mock_get.return_value = mock_response
        
        show_observed = Show_Observed(db)
        
        result = await show_observed.show_observed(update, context)
        
        assert result == ConversationHandler.END
        
        message = ""
        for token in tokens:
            message += f"{token['symbol']} - {current_price}\n"
        
        mock_get.assert_called_with(token['api_url'])
        reply_mock_text.assert_called_once_with(f"{message}")
    