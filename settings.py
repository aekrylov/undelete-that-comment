import os

from dotenv import load_dotenv
load_dotenv()

APP_ID = int(os.getenv('APP_ID'))
APP_TOKEN = os.getenv('APP_TOKEN')

BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_CHAT_ID = os.getenv('BOT_CHAT_ID')
