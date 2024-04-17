# DiscordRSSBot
A Discord bot that posts RSS feed updates of a Twitter user to a specified channel. The bot utilizes Nitter instances (Twitter front-ends focused on privacy) to fetch the RSS feed and send new tweets to the configured Discord channels.

## Features
- Fetch tweets from a specified Twitter account using RSS feeds from multiple Nitter instances
- Post new tweets to configured Discord channels
- Command to add or remove channels for receiving tweets
- Command to start, pause, restart, or force sending tweets
- Command to retrieve specific or all recent tweets
- Persistent storage of sent tweets using Firebase Realtime Database
- Customizable interval for checking for new tweets

## Limitations and Bugs
- The bot relies on the availability and reliability of Nitter instances, which may vary.
- The bot does not handle rate limiting or other potential issues that may arise from frequent requests to Nitter instances(there are multiple instances by default so it is not really a problem).
- The bot does not support direct Twitter integration and relies solely on RSS feeds provided by Nitter instances (Thanks to Elon Musk).

## Requirements
- Python 3.9+ (I haven't tested on previous 3. versions but it should work)
- Python modules listed in `requirements.txt`
- Discord bot token
- Firebase Realtime Database project with a service account key

## How it Works
1. The bot fetches the RSS feed of the specified Twitter account from multiple Nitter instances.
2. It compares the fetched tweets with the previously sent tweets stored in the Firebase Realtime Database.
3. New tweets are formatted and sent to the configured Discord channels.
4. The sent tweets are stored in the Firebase Realtime Database to avoid duplicates.
5. The process repeats at a specified interval.

## Usage
1. Set up a Discord bot and obtain its token.
2. Create a Firebase Realtime Database project and download the service account key.
3. Create a `.env` file with the required configuration variables (see the .env.example file).
4. Install the required Python modules: `pip install -r requirements.txt`
5. Run the bot: `python main.py`
6. Use the following commands in your Discord server (! is the prefix by default):
   - `!ping`: Test the bot's responsiveness.
   - `!addchannel <channel_mention>`: Add a channel to receive tweets.
   - `!removechannel <channel_id>`: Remove a channel from receiving tweets.
   - `!startrss`: Start the task of fetching and sending tweets.
   - `!pauserss`: Pause the tweet fetching and sending task.
   - `!restartrss`: Restart the tweet fetching and sending task.
   - `!getrss <range>`: Retrieve specific tweets (e.g., `!getrss 0-5` or `!getrss 3`).
   - `!getallrss`: Retrieve all recent tweets.
   - `!forcesend`: Force the bot to send tweets immediately.

## Permissions

The bot must have the following permissions:
- Send Messages
- Read Message History

## The bot in action
![image](https://i.imgur.com/rjhDeWw.png)

## License
Released under MIT. See `LICENSE` for details.
