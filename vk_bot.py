import vk_api as vk
from vk_api.exceptions import VkApiError
import random
from vk_api.longpoll import VkLongPoll, VkEventType
from telegram.ext import Updater
import os
from dotenv import load_dotenv
import logging


load_dotenv()

VK_ID = os.getenv('VK_ID')
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DIAG_BOT_ID = os.getenv("DIAG_BOT_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
LANG = 'en_US'

main_logger = logging.getLogger(__name__)


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def echo(event, vk_api):
    import dialogflow_v2 as dialogflow
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(DIAG_BOT_ID, VK_ID)

    text_input = dialogflow.types.TextInput(
            text=event.text, language_code=LANG)

    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(
            session=session, query_input=query_input)
    if not response.query_result.intent.is_fallback:        
        vk_api.messages.send(
            user_id=event.user_id,
            message=response.query_result.fulfillment_text,
            random_id=random.randint(1,1000)
        )

def main():

    main_logger.setLevel(logging.WARNING)
    updater = Updater(token=TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher
    telegram_handler = TelegramLogsHandler(dispatcher.bot, TELEGRAM_CHAT_ID)
    bot_message_format="%(asctime)s:[%(name)s]%(filename)s.%(funcName)s:%(levelname)s:%(message)s"
    formatter = logging.Formatter(bot_message_format)
    main_logger.addHandler(telegram_handler)
    telegram_handler.setFormatter(formatter)
    
    try:
        vk_session = vk.VkApi(token=VK_ID)
        vk_api = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                echo(event, vk_api)
    except VkApiError as vk_error:
        main_logger.warning(vk_error)

if __name__ == "__main__":
    main()