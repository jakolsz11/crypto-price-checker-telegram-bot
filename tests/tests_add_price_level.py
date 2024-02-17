import pytest
from unittest.mock import AsyncMock, patch, Mock, Mock
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram_commands.add_price_level_class import Add_Price_Level, CRYPTO_SYMBOL, PRICE_LEVEL, API_URL

class TestAddPriceLevel:
    @pytest.fixture
    def update_context(self):
        update = AsyncMock(spec=Update)
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        db = Mock()
        context.user_data = {}
        return update, context, db


    @pytest.mark.asyncio
    async def test_start_adding_price_level(self, update_context):
        update, context, db = update_context
        
        add_price_level = Add_Price_Level(db)

        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock

        result = await add_price_level.start_adding(update, context)
        assert result == CRYPTO_SYMBOL

        reply_text_mock.assert_called_once_with("Enter the symbol e.g. BTCUSDT")



    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_get_crypto_symbol_success(self, mock_get, update_context):
        crypto_symbol = 'BTC'
        update, context, db = update_context
        add_price_level = Add_Price_Level(db)
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        update.message.text = crypto_symbol

        mock_response = Mock()
        mock_response.json.return_value = {'price': 50000}
        mock_get.return_value = mock_response

        result = await add_price_level.get_crypto_symbol(update, context)

        assert result == PRICE_LEVEL

        assert context.user_data['crypto_symbol'] == crypto_symbol
        assert context.user_data['current_price'] == 50000

        mock_get.assert_called_once_with(f"{API_URL}{crypto_symbol}")
        
        reply_text_mock.assert_any_await(f"Specify the price level to observation for {crypto_symbol}")
        reply_text_mock.assert_any_await(f"{crypto_symbol}\nCurrent price: 50000")

    @pytest.mark.asyncio
    @patch('requests.get', side_effect=requests.RequestException)
    async def test_get_crypto_symbol_failure(self, mock_get, update_context):
        crypto_symbol = 'ETH'
        update, context, db = update_context
        add_price_level = Add_Price_Level(db)
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        update.message.text = crypto_symbol

        result = await add_price_level.get_crypto_symbol(update, context)

        assert result == ConversationHandler.END

        assert 'crypto_symbol' not in context.user_data
        assert 'current_price' not in context.user_data

        mock_get.assert_called_once_with(f"{API_URL}{crypto_symbol}")
        reply_text_mock.assert_any_await(f"{crypto_symbol} is unavailable.")

    @pytest.mark.asyncio
    async def test_get_price_level_new_price(self):
        update = AsyncMock(spec=Update)
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        
        context.user_data = {'crypto_symbol': 'BTC', 'current_price': '50000'}
        
        update.message.text = '10.5'
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        db = Mock() 
        db.find_one.return_value = {'_id': '65bee04c466bfd2b82aa7ad9', 'symbol': 'BTC', 'api_url': 'https://api.binance.us/api/v3/ticker/price?symbol=BTC', 'latest_price': '43000.32', 'reach': [5.0, 7.0, 8.0]}
        add_price_level = Add_Price_Level(db)
        
        result = await add_price_level.get_price_level(update, context)
        
        assert result == ConversationHandler.END
        
        reply_text_mock.assert_called_once_with(f'Price level added successfully!\nBTC\n10.5')
        
        
    @pytest.mark.asyncio
    async def test_get_price_level_exists(self):
        update = AsyncMock(spec=Update)
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        
        context.user_data = {'crypto_symbol': 'BTC', 'current_price': '50000'}
        
        update.message.text = '10.5'
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        db = Mock() 
        db.find_one.return_value = {'_id': '65bee04c466bfd2b82aa7ad9', 'symbol': 'BTC', 'api_url': 'https://api.binance.us/api/v3/ticker/price?symbol=BTC', 'latest_price': '43000.32', 'reach': [10.5, 5.0, 7.0, 8.0]}
        add_price_level = Add_Price_Level(db)
        
        result = await add_price_level.get_price_level(update, context)
        
        assert result == None
        
        keyboard = [
            [InlineKeyboardButton('Add another', callback_data='another', switch_inline_query_current_chat="button")],
            [InlineKeyboardButton('Cancel', callback_data='cancel', switch_inline_query_current_chat="button")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        reply_text_mock.assert_called_once_with(f'Price level is already added!', reply_markup=reply_markup)
        

    @pytest.mark.asyncio
    async def test_get_price_level_new_token(self, update_context):
        update, context, db = update_context
        
        context.user_data = {'crypto_symbol': 'BTC', 'current_price': '50000'}
        
        update.message.text = '10.5'
        
        db.find_one.return_value = None
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        
        add_price_level = Add_Price_Level(db)
        result = await add_price_level.get_price_level(update, context)
        assert result == ConversationHandler.END
        
        db.insert_one.assert_called_with(
            {
                'symbol': 'BTC',
                'api_url': 'https://api.binance.com/api/v3/ticker/price?symbol=BTC',
                'latest_price': 50000.0,
                'reach': [10.5]
            }
        )

        update.message.reply_text.assert_called_with(
            f'Price level added successfully!\n{context.user_data["crypto_symbol"]}\n10.5'
        )
        
        
    @pytest.mark.asyncio
    async def test_get_price_level_new_token_insert_error(self, update_context):
        update, context, db = update_context
        
        context.user_data = {'crypto_symbol': 'BTC', 'current_price': '50000'}
        
        update.message.text = '10.5'
        
        db.find_one.return_value = None
        db.insert_one.side_effect = Exception("Something went wrong during insert_one")
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        
        add_price_level = Add_Price_Level(db)
        
        await add_price_level.get_price_level(update, context)
        
        update.message.reply_text.assert_called_with("Sorry, something went wrong! Please try again later!")
    
    
    @pytest.mark.asyncio
    async def test_cancel_func(self, update_context):
        update, context, db = update_context
        add_price_level = Add_Price_Level(db)
        context.user_data = {'some_key': 'some_value'}
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock

        result = await add_price_level.cancel_adding(update, context)

        assert result == ConversationHandler.END

        update.message.reply_text.assert_called_once_with("Operation canceled.")

        assert not context.user_data
        

    @pytest.mark.asyncio
    async def test_price_level_callback_another(self, update_context):
        update, context, db = update_context
        add_price_level = Add_Price_Level(db)
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        reply_callback_query = AsyncMock()
        update.callback_query = reply_callback_query
        
        query = update.callback_query
        
        query.data = 'another'
        context.user_data = {'crypto_symbol': 'BTC'}
        
        result = await add_price_level.add_price_level_callback(update, context)
        
        query.answer.assert_awaited_once()
        
        assert result == PRICE_LEVEL
        
        query.edit_message_text.assert_called_once_with(f"Specify the price level to observation for {context.user_data['crypto_symbol']}")


    @pytest.mark.asyncio
    async def test_price_level_callback_cancel(self, update_context):
        update, context, db = update_context
        add_price_level = Add_Price_Level(db)
        
        reply_text_mock = AsyncMock()
        update.message.reply_text = reply_text_mock
        
        reply_callback_query = AsyncMock()
        update.callback_query = reply_callback_query
        
        query = update.callback_query
        
        query.data = 'cancel'
        context.user_data = {'crypto_symbol': 'BTC'}
        
        result = await add_price_level.add_price_level_callback(update, context)
        
        query.answer.assert_awaited_once()
        
        assert result == ConversationHandler.END
        
        query.edit_message_text.assert_called_once_with("Operation canceled.")
        assert not context.user_data
    
    