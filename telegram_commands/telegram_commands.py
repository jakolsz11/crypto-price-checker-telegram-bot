from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, CallbackQueryHandler
from connectDB import connectDB
from add_price_level_class import Add_Price_Level
from add_to_observed_class import Add_To_Observed
from delete_price_level_class import Delete_Price_Level
from delete_observed_class import Delete_Observed
from show_observed_class import Show_Observed
from show_price_levels_class import Show_Price_Levels

db_tokens = connectDB('tokens')
db_observed = connectDB('observed_tokens')


BOT_TOKEN = "6930544388:AAFm0rjAWeLQodSWZ4xUA1lzcoR6foNjVx0"
CRYPTO_SYMBOL, PRICE_LEVEL, CHOOSE_SYMBOL, DELETE_COMMAND, END_QUESTION, GET_LEVELS, GET_TOKEN_OBSERVED, DELETE_OBSERVED, END_QUESTION = 1, 2, 3, 4, 5, 6, 7, 8, 9

def main() -> None:
    print("Starting bot...")
    application = Application.builder().token(BOT_TOKEN).build()
    
    add_price_level = Add_Price_Level(db_tokens)
    
    add_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('addpricelevel', add_price_level.start_adding)],
        states={
            CRYPTO_SYMBOL: [MessageHandler(filters.TEXT & (~ filters.COMMAND), add_price_level.get_crypto_symbol)],
            PRICE_LEVEL: [MessageHandler(filters.TEXT & (~ filters.COMMAND), add_price_level.get_price_level), CallbackQueryHandler(add_price_level.add_price_level_callback)]
        },
        fallbacks=[CommandHandler('cancel', add_price_level.cancel_adding)],
        allow_reentry=True,
    )
    
    delete_price_level = Delete_Price_Level(db_tokens)
    
    delete_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('deletepricelevel', delete_price_level.delete_price_level)],
        states = {
            CHOOSE_SYMBOL: [CallbackQueryHandler(delete_price_level.choose_level_callback)],
            DELETE_COMMAND: [CallbackQueryHandler(delete_price_level.delete_price_level_callback)]
        },
        fallbacks=[CommandHandler('cancel', add_price_level.cancel_adding)],
        allow_reentry=True
    )
    
    show_price_levels = Show_Price_Levels(db_tokens)
    
    show_price_levels_conversation = ConversationHandler(
        entry_points=[CommandHandler('showpricelevels', show_price_levels.show_price_levels)],
        states = {
            GET_LEVELS: [CallbackQueryHandler(show_price_levels.show_price_levels_callback)]
        },
        fallbacks=[CommandHandler('cancel', add_price_level.cancel_adding)],
        allow_reentry=True
    )
    
    add_to_observed = Add_To_Observed(db_observed)
    
    add_to_observed_conversation = ConversationHandler(
        entry_points=[CommandHandler('addtoobserved', add_to_observed.start_add_to_observed)],
        states={
            GET_TOKEN_OBSERVED: [MessageHandler(filters.TEXT & (~ filters.COMMAND), add_to_observed.add_to_observed)]
        },
        fallbacks=[CommandHandler('cancel', add_price_level.cancel_adding)],
        allow_reentry=True
    )
    
    delete_observed =  Delete_Observed(db_observed)
    
    delete_observed_conversation = ConversationHandler(
        entry_points=[CommandHandler('deletefromobserved', delete_observed.delete_observed_token)],
        states={
            DELETE_OBSERVED: [CallbackQueryHandler(delete_observed.delete_observed_token_callback)],
            END_QUESTION: [CallbackQueryHandler(delete_observed.end_question_callback)]
        },
        fallbacks=[CommandHandler('cancel', add_price_level.cancel_adding)],
        allow_reentry=True
    )
    
    application.add_handler(add_conversation_handler)
    application.add_handler(delete_conversation_handler)
    application.add_handler(show_price_levels_conversation)
    application.add_handler(add_to_observed_conversation)
    application.add_handler(delete_observed_conversation)
    
    show_observed = Show_Observed(db_observed)    
    application.add_handler(CommandHandler('showobserved', show_observed.show_observed))
    
    print("Pooling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == "__main__":
    main()