import json
import os
import dialogflow_v2 as dialogflow
import google.api_core.exceptions as google_ex
from dotenv import load_dotenv

INTENTS_FILE_NAME = 'example_questions.json'


def get_intens(intents_file_name):
    with open(intents_file_name) as intents_file:
        intents = json.load(intents_file)
    return intents


def create_dialog_flow_intent(intent_name, intent_content):
    intent = {
        'display_name': intent_name,
        'messages': [
            {
                'text': {
                    'text': [
                        intent_content['answer'],
                    ],
                },
            },
        ],
        'training_phrases': [{"parts": [{"text": phrases}]} for phrases in intent_content['questions']]
    }
    return intent



def main():

    load_dotenv()
    DIAG_BOT_ID = os.getenv("DIAG_BOT_ID")

    intents = get_intens(INTENTS_FILE_NAME)
    for intent_name, intent_content in intents.items():
        try:
            dialog_flow_intent = create_dialog_flow_intent(intent_name, intent_content)
            intent_clt = dialogflow.IntentsClient()
            parent = intent_clt.project_agent_path(DIAG_BOT_ID)
            intent_clt.create_intent(parent, dialog_flow_intent)
        except google_ex.InvalidArgument:
            pass
        
    agent = dialogflow.AgentsClient()
    parent = agent.project_path(DIAG_BOT_ID)
    agent.train_agent(parent)


if __name__ == "__main__":
    main()

