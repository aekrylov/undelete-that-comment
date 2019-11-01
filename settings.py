import os

from dotenv import load_dotenv

# Load properties into os.environ from .env file, if present
load_dotenv()

APP_ID = int(os.getenv('APP_ID'))  # VK standalone app id
APP_TOKEN = os.getenv('APP_TOKEN')  # A service token is enough

BOT_TOKEN = os.getenv('BOT_TOKEN')  # Bot token from the BotFather
BOT_CHAT_ID = os.getenv('BOT_CHAT_ID')  # Either chat id or a @channel-name, bot should have write access to it
