import vk_api as vk
import random
from vk_api.longpoll import VkLongPoll, VkEventType
import os

VK_ID = os.getenv('VK_ID')
DIAG_BOT_ID = os.getenv("DIAG_BOT_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
LANG = 'en_US'


def echo(event, vk_api):
    import dialogflow_v2 as dialogflow
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(DIAG_BOT_ID, VK_ID)
    print('Session path: {}  {}\n'.format(session, event.text))

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


if __name__ == "__main__":
    vk_session = vk.VkApi(token=VK_ID)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            echo(event, vk_api)