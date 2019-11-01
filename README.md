# Undelete that comment!

This tool helps detecting insincere behaviors on the internet by notifying about 
deleted comments in discussions.

Supported inputs:

* [VK](https://vk.com) discussion boards (works as a standalone app)

Supported outputs:

* Telegram channels and private chats (works as a bot)

## How to run

1. Create a Standalone VK application [here](https://vk.com/editapp?act=create)
and get your app id and Service key
2. Create a Telegram bot with @BotFather
3. Setup your `.env` file as per [template](./.env.template), 
or put everything into environment variables
4. Run
```shell script
python3 crawler.py
```