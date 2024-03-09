# EDIT THE CONFIG HERE #

# Discord IDs
# Replace values with your own.
MUDAE_ID = 432610292342587392  # ID of Mudae bot
CHANNEL_ID = 1059813170589479016  # ID of claiming channel
SERVER_ID = 1059813170589479013  # ID of Discord server
USER_ID = 1129120966954451168  # ID of main user

# Bot token
BOT_TOKEN = ""

# Command prefix for Mudae and roll command to use.
# Default setting below does $m
COMMAND_PREFIX = "$"
ROLL_COMMAND = "m"

#  User login info.
#  This is not sent to any external server, but only uses to login to browser Discord.
#  See Browser.browser_login() (specifically line 58-61) in browsers.py to see how it is exactly used.
LOGIN_INFO = ("arturotevallas@gmail.com", "Thdg1988")

# Time between claim resets, in minutes.
CLAIM_DURATION = 180

# Time between roll resets, in minutes.
# Set to 0 to disable auto rolls.
ROLL_DURATION = 60

# Time between daily command resets, in minutes.
# Set to 0 to disable auto dailies.
DAILY_DURATION = 1200

# Time between kakera loot resets, in minutes. Set to 0 to always attempt kakera loot.
# Note that the kakera power usage algorithms make this somewhat more complex than a simple "reset".
# For example, if each kakera loot uses %60 power, the first loot would take 1 hour to reset.
# The next loot would take 3 hours.
# Usually 1 hour is sufficient.
KAKERA_DURATION = 60

# Maximum number of rolls per reset.
MAX_ROLLS = 10

# Set True to roll every interval despite having claims or not.
ALWAYS_ROLL = False

LOG_FILE = "./log.txt"


# SELENIUM CONFIG INFO #
# On Ubuntu, run:
# $ sudo apt update
# $ sudo apt install geckodriver
# On Windows, download from https://github.com/mozilla/geckodriver/releases and extract the Windows version
# Make sure to use double backslashes "\\" in Windows when typing paths
# Ex. "C:\\Program Files\\Mozilla Firefox\\geckodriver.exe"
# On Linux, single forward slashes are okay.
# Ex. "/usr/bin/geckodriver"
# Set to None if geckodriver is in the PATH
WEB_DRIVER_PATH = "/usr/bin/geckodriver"
