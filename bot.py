 
from asyncio import TimeoutError
import discord
import sys
import re
from concurrent.futures import ThreadPoolExecutor
import threading
import logging
import datetime
import aiohttp
import config
from browsers import Browser
from timers import Timer

# noinspection PyArgumentList
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(config.LOG_FILE, 'a', 'utf-8'),
        logging.StreamHandler(sys.stdout)
    ])

# Initialize Selenium browser integration in separate module
browser = Browser()

# Declare global timer module
timer: Timer

# Main thread and Discord bot integration here
client = discord.Client()
main_user: discord.User
dm_channel: discord.DMChannel
roll_channel: discord.TextChannel
mudae: discord.Member
ready = False

# To be parsed by $tu and used for the auto roller
timing_info = {
    'claim_reset': None,
    'claim_available': None,
    'rolls_reset': None,
    'kakera_available': None,
    'kakera_reset': None,
    'daily_reset': None
}


async def close_bot():
    await client.close()
    client.loop.stop()
    client.loop.close()
    sys.exit()


@client.event
async def on_ready():
    # Ensure the browser is ready before proceeding (blocking call)
    try:
        browser_login.result()
    except TimeoutError or ValueError:
        await close_bot()

    def parse_tu(message):
        global timing_info
        if message.channel != roll_channel or message.author != mudae: return
        match = re.search(r"""^.*?(\w+).*?                                  # Group 1: Username
                                (can't|can).*?                              # Group 2: Claim available
                                (\d+(?:h\ \d+)?)(?=\*\*\ min).*?            # Group 3: Claim reset
                                (\d+(?:h\ \d+)?)(?=\*\*\ min).*?            # Group 4: Rolls reset
                                (?<=\$daily).*?(available|\d+h\ \d+).*?     # Group 5: $daily reset
                                (can't|can).*?(?=react).*?                  # Group 6: Kakera available
                                (?:(\d+(?:h\ \d+)?)(?=\*\*\ min)|(now)).*?  # Group 7: Kakera reset
                                (?<=\$dk).*?(ready|\d+h\ \d+)               # Group 8: $dk reset
                                .*$                                         # End of string
                                """, message.content, re.DOTALL | re.VERBOSE)
        if not match: return
        if match.group(1) != main_user.name: return
        # Convert __h __ to minutes
        times = []
        for x in [match.group(3), match.group(4), match.group(5), match.group(7)]:
            # Specifically, group 7 may be None if kakera is ready
            if x is None:
                x = 0
            elif 'h ' in x:
                x = x.split('h ')
                x = int(x[0]) * 60 + int(x[1])
            elif x == 'ready' or x == 'now':
                x = 0
            else:
                x = int(x)
            times.append(x)
        kakera_available = match.group(6) == 'can'
        claim_available = match.group(2) == 'can'
        timing_info = {
            'claim_reset': datetime.datetime.now() + datetime.timedelta(minutes=times[0]),
            'claim_available': claim_available,
            'rolls_reset': datetime.datetime.now() + datetime.timedelta(minutes=times[1]),
            'kakera_available': kakera_available,
            'kakera_reset': datetime.datetime.now() + datetime.timedelta(minutes=times[3]),
            'daily_reset': datetime.datetime.now() + datetime.timedelta(minutes=times[2]),
        }
        return True

    global main_user, mudae, dm_channel, roll_channel, timer, timing_info, ready
    logging.info(f'Bot connected as {client.user.name} with ID {client.user.id}')
    main_user = await client.fetch_user(config.USER_ID)
    dm_channel = await main_user.create_dm()
    roll_channel = await client.fetch_channel(config.CHANNEL_ID)
    mudae = await client.fetch_user(config.MUDAE_ID)

    # Parse timers by sending $tu command
    # Only do so once by checking ready property
    if not ready:
        logging.info('Attempting to parse $tu command')
        pool.submit(Browser.send_text, browser, f'{config.COMMAND_PREFIX}tu')
        try:
            await client.wait_for('message', check=parse_tu, timeout=3)
        except TimeoutError:
            logging.critical('Could not parse $tu command, quitting (try again)')
            browser.close()
            await close_bot()
        else:
            logging.info('$tu command parsed')
            logging.info('Creating new Timer based on parsed information')
            timer = Timer(browser, timing_info["claim_reset"], timing_info["rolls_reset"], timing_info["daily_reset"],
                          timing_info['claim_available'], timing_info["kakera_reset"], timing_info["kakera_available"])

            if config.DAILY_DURATION > 0:
                threading.Thread(name='daily', target=timer.wait_for_daily).start()
            if config.ROLL_DURATION > 0:
                threading.Thread(name='roll', target=timer.wait_for_roll).start()
            threading.Thread(name='claim', target=timer.wait_for_claim).start()
            threading.Thread(name='kakera', target=timer.wait_for_kakera).start()

            # For some reason, browser Discord crashes sometime at this point
            # Refresh the page to fix
            browser.refresh()  # Blocking call
            logging.info("Listener is ready")
            ready = True


@client.event
async def on_message(message):
    def parse_embed():
        # Regex based parsing adapted from the EzMudae module by Znunu
        # https://github.com/Znunu/EzMudae
        desc = embed.description
        name = embed.author.name
        series = None
        owner = None
        key = False

        # Get series and key value if present
        match = re.search(r'^(.*?[^<]*)(?:<:(\w+key))?', desc, re.DOTALL)
        if match:
            series = match.group(1).replace('\n', ' ').strip()
            if len(match.groups()) == 3:
                key = match.group(2)

        # Check if it was a roll
        # Look for any
        match = re.search(r'(?<=\*)(\d+)', desc, re.DOTALL)
        if match: return

        # Check if valid parse
        if not series: return

        # Get owner if present
        if not embed.footer.text:
            is_claimed = False
        else:
            match = re.search(r'(?<=Belongs to )\w+', embed.footer.text, re.DOTALL)
            if match:
                is_claimed = True
                owner = match.group(0)
            else:
                is_claimed = False

        # Log in roll list and console/logfile
        with open('./data/rolled.txt', 'a') as f:
            f.write(f'{datetime.datetime.now()}    {name} - {series}\n')

        logging.info(f'Parsed roll: {name} - {series} - Claimed: {is_claimed}')

        return {'name': name,
                'series': series,
                'is_claimed': is_claimed,
                'owner': owner,
                'key': key}

    def reaction_check(payload):
        # Return if reaction message or author incorrect
        if payload.message_id != message.id: return
        if payload.user_id != mudae.id: return

        # Open thread to click emoji
        emoji = payload.emoji
        pool.submit(browser.react_emoji, emoji.name, message.id)
        return True

    ## BEGIN ON_MESSAGE BELOW ##
    global main_user, mudae, dm_channel, roll_channel, ready
    if not ready: return

    # Only parse messages from the bot in the right channel that contain a valid embed
    if message.channel != roll_channel or message.author != mudae or not len(message.embeds) == 1 or \
            message.embeds[0].image.url == message.embeds[0].Empty: return

    embed = message.embeds[0]
    if not (waifu_result := parse_embed()): return  # Return if parsing failed

    # If unclaimed waifu was on likelist
    if waifu_result['name'] in like_array and not waifu_result['is_claimed']:
        if not timer.get_claim_availability():  # No claim is available
            logging.warning(f'Character {waifu_result["name"]} was on the likelist but no claim was available!')
            await dm_channel.send(content=f"Character {waifu_result['name']} was on the likelist"
                                          f"but no claim was available!", embed=embed)
            return

        logging.info(f'Character {waifu_result["name"]} in likelist, attempting marry')

        # New Mudae bot does not automatically add emojis, just react.
        pool.submit(browser.react_emoji, "❤", message.id)

        """
        try:
            await client.wait_for('raw_reaction_add', check=reaction_check, timeout=3)
        except TimeoutError:
            logging.critical('Marry failed, could not detect bot reaction')
            return
        else:
            await dm_channel.send(content=f"Marry attempted for {waifu_result['name']}", embed=embed)
            timer.set_claim_availability(False)
        """

    # If key was rolled
    if waifu_result['owner'] == main_user.name and waifu_result['key']:
        await dm_channel.send(content=f"{waifu_result['key']} rolled for {waifu_result['name']}", embed=embed)

    # If kakera loot available
    if waifu_result['is_claimed']:
        if not timer.get_kakera_availablilty():
            logging.warning(f'Character {waifu_result["name"]} has kakera loot but the loot was not available!')
            await dm_channel.send(content=f"Character {waifu_result['name']} had kakera loot"
                                          f" but no loot was available!", embed=embed)
            return
        logging.info('Attempting to loot kakera')
        try:
            await client.wait_for('raw_reaction_add', check=reaction_check, timeout=3)
        except TimeoutError:
            logging.critical('Kakera loot failed, could not detect bot reaction')
            return
        else:
            await dm_channel.send(content=f"Kakera loot attempted for {waifu_result['name']}", embed=embed)
            timer.set_kakera_availability(False)

def init():
    if __name__ == '__main__':
        with open('./data/likelist.txt', 'r') as f:
            logging.info('Parsing likelist')
            like_array = [x.strip() for x in [x for x in f.readlines() if not x.startswith('\n')] if not x.startswith('#')]
        pool = ThreadPoolExecutor()
        try:
            logging.info('Starting browser thread')
            browser_login = pool.submit(Browser.browser_login, browser)
            client.loop.run_until_complete(client.start(config.BOT_TOKEN))
        except KeyboardInterrupt:
            logging.critical("Keyboard interrupt, quitting")
            client.loop.run_until_complete(client.logout())
        except discord.LoginFailure or aiohttp.ClientConnectorError:
            logging.critical(f"Improper token has been passed or connection to Discord failed, quitting")
        finally:
            browser.close()
            client.loop.stop()
            client.loop.close()
    else:
        with open('./data/likelist.txt', 'r') as f:
            logging.info('Parsing likelist')
            like_array = [x.strip() for x in [x for x in f.readlines() if not x.startswith('\n')] if not x.startswith('#')]
        pool = ThreadPoolExecutor()
        try:
            logging.info('Starting browser thread')
            browser_login = pool.submit(Browser.browser_login, browser)
            client.loop.run_until_complete(client.start(config.BOT_TOKEN))
        except KeyboardInterrupt:
            logging.critical("Keyboard interrupt, quitting")
            client.loop.run_until_complete(client.logout())
        except discord.LoginFailure or aiohttp.ClientConnectorError:
            logging.critical(f"Improper token has been passed or connection to Discord failed, quitting")
        finally:
            browser.close()
            client.loop.stop()
            client.loop.close()

init()