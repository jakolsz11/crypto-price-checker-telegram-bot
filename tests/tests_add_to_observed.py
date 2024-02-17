import pytest
from unittest.mock import AsyncMock, patch, Mock, Mock
from telegram import Update
from telegram.ext import ConversationHandler, ContextTypes
import requests
from telegram_commands.add_to_observed_class import Add_To_Observed, GET_TOKEN_OBSERVED, API_URL

class TestAddToObserved:
    @pytest.fixture
    def update_context_db(self):
        update = AsyncMock(spec=Update)
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        db = Mock()
        return update, context, db
    

    @pytest.mark.asyncio
    async def test_start_add_to_observed(self, update_context_db):
        update, context, db = update_context_db
        
        add_to_observed = Add_To_Observed(db)
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        result = await add_to_observed.start_add_to_observed(update, context)
        
        assert result == GET_TOKEN_OBSERVED
        
        reply_text_mock.assert_called_once_with("Enter the token symbol!")
        
    
    @pytest.mark.asyncio
    @patch('requests.get', side_effect=requests.RequestException)
    async def test_add_to_observed_failure(self, mock_get, update_context_db):
        update, context, db = update_context_db
        token_symbol = "BTC"
        
        add_to_observed = Add_To_Observed(db)
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        update.message.text = token_symbol
        
        result = await add_to_observed.add_to_observed(update, context)
        
        mock_get.assert_called_once_with(f"{API_URL}{token_symbol}")
        reply_text_mock.assert_called_once_with(f"{token_symbol} is unavailable.")
        
        assert result == ConversationHandler.END
        
        
    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_add_to_observed_success_new_token(self, mock_get, update_context_db):
        update, context, db = update_context_db
        token_symbol = "BTC"
        current_price = 50000
        
        add_to_observed = Add_To_Observed(db)
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        update.message.text = token_symbol
        
        mock_response = Mock()
        mock_response.json.return_value = {'price': current_price}
        mock_get.return_value = mock_response
        
        db.find_one.return_value = None
        
        result = await add_to_observed.add_to_observed(update, context)
        
        db.insert_one.assert_called_with(
            {
                "symbol": token_symbol,
                "api_url": f"{API_URL}{token_symbol}"
            }
        )
        
        mock_get.assert_called_once_with(f"{API_URL}{token_symbol}")
        reply_text_mock.assert_called_once_with(f"{token_symbol} successfully added to observed!\nCurrent price is {current_price}")
        
        assert result == ConversationHandler.END
        
        
    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_add_to_observed_success_token_exists(self, mock_get, update_context_db):
        update, context, db = update_context_db
        token_symbol = "BTC"
        
        add_to_observed = Add_To_Observed(db)
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        update.message.text = token_symbol
        
        db.find_one.return_value = {'symbol': token_symbol}
        
        current_price = 50000
        mock_response = Mock()
        mock_response.json.return_value = {'price': current_price}
        mock_get.return_value = mock_response
        
        result = await add_to_observed.add_to_observed(update, context)
        
        mock_get.assert_called_once_with(f"{API_URL}{token_symbol}")
        reply_text_mock.assert_called_once_with(f"{token_symbol} is already observed!\nCurrent price is {current_price}")
        
        assert result == ConversationHandler.END
        
        
