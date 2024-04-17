# DiscordRSSBot
A Discord bot that posts RSS feed updates of a twitter user to a channel.

## The bot in action
![image](https://i.imgur.com/rjhDeWw.png)

## Features

## Limitations and bugs
 

## Requirements
- Python 3.9+ (haven't tested on previous 3. versions but it should work)
- Python modules: see `requirements.txt`

## How it works

 
## Usage
Set up a Discord bot and obtain its token.
Create a Firebase Realtime Database project and download the service account key.
Create a .env file with the required configuration variables (see the example in the code).
Install Python 3.8+ and required modules. Optionally make a new virtual environment for it.
`pip install -r requirements.txt`
To start the bot, run `main.py` `python main.py`
Use the following commands in your Discord server (! is the prefix by default):
* !ping: Test the bot's responsiveness.
* !addchannel <channel_mention>: Add a channel to receive tweets.
* !removechannel <channel_id>: Remove a channel from receiving tweets.
* !startrss: Start the task of fetching and sending tweets.
* !pauserss: Pause the tweet fetching and sending task.
* !restartrss: Restart the tweet fetching and sending task.
* !getrss <range>: Retrieve specific tweets (e.g., !getrss 0-5 or !getrss 3).
* !getallrss: Retrieve all recent tweets.
* !forcesend: Force the bot to send tweets immediately.

The bot must have the following permissions:
- Send Messages
- Read Message History

## License
Released under MIT. See `LICENSE` for details.
