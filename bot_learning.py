import json
import os
import dialogflow_v2 as dialogflow
import google.api_core.exceptions as google_ex
from dotenv import load_dotenv


load_dotenv()

DIAG_BOT_ID = os.getenv("DIAG_BOT_ID")
QUESTIONS_FILE_NAME = 'example_questions.json'


def get_questions(questions_file_name):
    with open(questions_file_name) as questions_file:
        questions = json.load(questions_file)
    return questions


def create_intent(questions, intent_name):
    intent = {
        'display_name':
        intent_name,
        'messages': [
            {
                'text': {
                    'text': [
                        questions[intent_name]['answer'],
                    ],
                },
            },
        ],
        'training_phrases': [],
    }
    for question in questions[intent_name]['questions']:
        cur_quest = {
            'parts': [
                {'text': question,},
            ],
        }
    
        intent['training_phrases'].append(cur_quest)
    return intent



def main():
    questions = get_questions(QUESTIONS_FILE_NAME)
    for quest in questions:
        try:
            intent = create_intent(questions, quest)
            intent_clt = dialogflow.IntentsClient()
            parent = intent_clt.project_agent_path(DIAG_BOT_ID)
            intent_clt.create_intent(parent, intent)
        except google_ex.InvalidArgument:
            pass
        
    agent = dialogflow.AgentsClient()
    parent = agent.project_path(DIAG_BOT_ID)
    agent.train_agent(parent)


if __name__ == "__main__":
    main()

