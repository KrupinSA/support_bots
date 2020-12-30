import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DIAG_BOT_ID = os.getenv("DIAG_BOT_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
LANG = 'en_US'

logging.basicConfig(format="%(asctime)s:[%(name)s]%(filename)s.%(funcName)s:%(levelname)s:%(message)s")
main_logger = logging.getLogger(__name__)

class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def detect_intent_texts(bot, update):
    import dialogflow_v2 as dialogflow
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(DIAG_BOT_ID, TELEGRAM_TOKEN)

    text_input = dialogflow.types.TextInput(
            text=update.message.text, language_code=LANG)

    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(
            session=session, query_input=query_input)

    if not response.query_result.intent.is_fallback: 
        update.message.reply_text(response.query_result.fulfillment_text)

def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Здравствуйте!')

def error_to_logger(bot, update, err_mess):
    main_logger.warning(f'Update {update} caused error {err_mess}')

def main():
    
    main_logger.setLevel(logging.WARNING)

    updater = Updater(token=TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    telegram_handler = TelegramLogsHandler(dispatcher.bot, TELEGRAM_CHAT_ID)
    main_logger.addHandler(telegram_handler)

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text, detect_intent_texts))

    dispatcher.add_error_handler(error_to_logger)

    updater.start_polling()
    updater.idle()


if __name__=="__main__":
    main()