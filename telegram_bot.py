import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DIAG_BOT_ID = os.getenv("DIAG_BOT_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
LANG = 'en_US'

main_logger = logging.getLogger(__name__)

def detect_intent_texts(bot, update):
    import dialogflow_v2 as dialogflow
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(DIAG_BOT_ID, TELEGRAM_TOKEN)
    print('Session path: {}  {}\n'.format(session, update.message.text))

    text_input = dialogflow.types.TextInput(
            text=update.message.text, language_code=LANG)

    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(
            session=session, query_input=query_input)

    print('=' * 20)
    print('Query text: {}'.format(response.query_result.query_text))
    print('Detected intent: {} (confidence: {})\n'.format(
            response.query_result.intent.display_name,
            response.query_result.intent_detection_confidence))
    print('Fulfillment text: {}\n'.format(
            response.query_result.fulfillment_text))
        
    update.message.reply_text(response.query_result.fulfillment_text)

def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Здравствуйте!')

def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def error_to_logger(bot, update, err_mess):
    main_logger.warning(f'Update {update} caused error {err_mess}')

def main():
    #Init logginig to console
    message_format = "%(asctime)s:[%(name)s]%(filename)s.%(funcName)s:%(levelname)s:%(message)s"
    level = logging.WARNING
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(message_format)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    main_logger.addHandler(console_handler)

    updater = Updater(token=TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text, detect_intent_texts))

    # log all errors
    dispatcher.add_error_handler(error_to_logger)

    updater.start_polling()
    updater.idle()


if __name__=="__main__":
    main()