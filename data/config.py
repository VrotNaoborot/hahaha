from pathlib import Path
import logging
from fake_useragent import UserAgent

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

ua = UserAgent(platforms='desktop', browsers=['Chrome'])

CONFIG_DIR = Path(__file__).resolve().parent

EXTENSION_PATH = CONFIG_DIR / 'alpha'
SESSION_PATH = CONFIG_DIR / 'sessions'
ACCOUNTS_PATH = CONFIG_DIR / 'accounts.csv'
ACCOUNT_CHECK_INTERVAL = [1000, 5000]  # seconds

NOT_FOUND_SLEEP_START = 5  # seconds

SITES_FARM_COOKIES = [
    "https://ebay.com",
    "https://columbia.com",
    "https://boscovs.com",
    "https://zappos.com",
    "https://asos.com",
    "https://nflgamepass.com",
    "https://edition.cnn.com/specials/travel/cnngo-travel",
    "https://abc.com",
    "https://cbs.com",
    "https://smithsonianchannel.com",
    "https://apple.com/retail/mallofamerica",
    "https://yahoo.com",
    "https://msn.com",
    "https://microsoft.com",
    "https://realtor.com",
    "https://zillow.com",
    "https://trulia.com",
    "https://homes.com",
    "https://iaai.com",
    "https://copart.com",
    "https://youtube.com",
    "https://twitter.com",
    "https://facebook.com",
    "https://twitch.tv",
    "https://world.taobao.com",
    "https://bhphotovideo.com",
    "https://chinavasion.com"
]
