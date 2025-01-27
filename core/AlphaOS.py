import asyncio
import random
from typing import Optional
from utils.exeptions_os import *
from utils.data_change import *
import time
import logging

from patchright.async_api import *
from data.config import *
from colorama import Fore
from fake_useragent import UserAgent

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

ua = UserAgent(platforms='desktop', browsers=['Chrome'])

gen_ua = ua.random
logger.info(f"generated ua - {gen_ua}")


def try_parse_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


class AlphaOS:
    def __init__(self, id: str, mail: str, proxy: str, extension_id: str):
        self.id = id
        self.mail = mail
        self.proxy = {
            'server': f'http://{proxy.split(":")[0]}:{proxy.split("@")[0].split(":")[1]}',
            'username': f'{proxy.split("@")[1].split(":")[0]}',
            'password': f'{proxy.split("@")[1].split(":")[1]}',
        }
        self.browser: Optional[Browser] = None
        logger.info(f"Account: {self.mail} AlphaOS instance created for account")
        self.extension_id = extension_id

    async def farm_cookies(self):
        logger.info(f"Account: {self.mail} Cookie farm start.")
        await self._initialize_browser()
        selected_sites = random.sample(SITES_FARM_COOKIES, random.randint(5, len(SITES_FARM_COOKIES)))

        for site in selected_sites:
            await self._visit_site(site)
        await self.browser.close()
        logger.info(f"Account: {self.mail} Cookie farm is finished.")

    async def _visit_site(self, url):
        try:
            page = await self.browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state('load')
            # scroll down
            for i in range(10):
                await page.mouse.wheel(0, 300)
                await asyncio.sleep(0.5)

            await page.close()
        except Exception as ex:
            logger.error(f"Account: {self.mail} broke farm site: {url}. Ex: {ex}")

    async def take_extension_id(self) -> str:
        """take and save ex_id"""
        try:
            page = await self.browser.new_page()
            await page.goto("chrome://extensions/")
            await page.wait_for_selector("body")
            dev_mode = page.locator("#devMode")
            await dev_mode.wait_for()

            print(f"att - {await dev_mode.get_attribute('aria-pressed')}")
            if await dev_mode.get_attribute('aria-pressed') == "false":
                await page.locator("#devMode").click()
                logger.info(f"Account: {self.mail} devMode click")

            extension_id = await page.locator("#extension-id").text_content()
            extension = extension_id.split(":")[1].strip()
            await save_ex_id(extension_id=extension, user_id=self.id)
            logger.info(f"Account: {self.mail} get extension - {extension_id}")
            return extension
        except PermissionError as ex:
            logger.error(f"Account: {self.mail} {ex}")
        except Exception as ex:
            logger.error(f"Account: {self.mail} {ex}")

    async def work(self):
        try:
            await self._initialize_browser()
            if not self.extension_id:
                self.extension_id = await self.take_extension_id()
            await self.browser.new_page()
            page = await self.browser.new_page()

            if not self.extension_id:
                self.extension_id = await self.take_extension_id()

            not_found_sleep = NOT_FOUND_SLEEP_START

            while True:
                try:
                    await page.goto(f'chrome-extension://{self.extension_id}/popup.html')
                    logger.info(f'{self.mail} Load popup')

                    await page.wait_for_load_state('load')
                    await asyncio.sleep(random.randint(5, 10))
                    await page.locator('xpath=//*[@id="__plasmo"]/span/span/div/div[1]/div[1]/div[1]').click()
                    logger.info(f'{self.mail} Load mining page')

                    await page.wait_for_load_state('load')
                    await asyncio.sleep(random.randint(1, 3))

                    button_locator_login = page.locator('button', has_text='Sign-In / Sign-Up')

                    if await button_locator_login.is_visible():
                        raise UnauthorizedError("User not login")

                    button_start_mining = page.locator('button', has_text='Start Mining')
                    button_stop_mining = page.locator('button', has_text='Stop Mining')

                    if await button_start_mining.count() > 0:
                        await button_start_mining.click()
                        logger.info(f"Account: {self.mail} Start mining.")
                    elif await button_stop_mining.count() > 0:
                        logger.info(f"Account: {self.mail} Mining is already in progress.")
                    else:
                        logger.error(
                            f"Account: {self.mail} Buttons start/stop not found. Sleep delay: {not_found_sleep}")
                        await asyncio.sleep(not_found_sleep)
                        not_found_sleep *= 2
                        continue

                    mining_points = await page.locator(
                        'xpath=//*[@id="__plasmo"]/span/span/div/div[2]/div/div[2]/span[1]/span').inner_text()
                    total_balance = await page.locator(
                        '//*[@id="__plasmo"]/span/span/div/div[2]/div/div[1]/span[2]').inner_text()

                    time_sleep_interval = random.randint(ACCOUNT_CHECK_INTERVAL[0], ACCOUNT_CHECK_INTERVAL[1])
                    logger.info(
                        f"Account: {self.mail} | Ready to claim: {mining_points} | Total balance: {total_balance} | Sleep: {time_sleep_interval} sec.")
                    if try_parse_int(mining_points) > 0:
                        await page.locator('button', has_text='Claim').click()
                        logger.info(f'Account: {self.mail} | Claim click.')
                    await asyncio.sleep(time_sleep_interval)
                except UnauthorizedError:
                    logger.error(f"Account: {self.mail} is not authorized! Account discconected")
                    await self.browser.close()
                    return
                except TimeoutError as e:
                    logger.error(f"Account: {self.mail} not found item. Try again... \n{e}")
                    await asyncio.sleep(not_found_sleep)
                    not_found_sleep *= 2
                    continue
        except Exception as ex:
            logger.error(f"Account: {self.mail} Err: {ex}")
            return

    async def create_profile_and_login(self):
        logger.info(f"Account: {self.mail} login...")
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=SESSION_PATH / f"{self.mail.split('@')[0]}",
                headless=True,
                proxy=self.proxy,
                args=[
                    f"--disable-extensions-except={EXTENSION_PATH}",
                    f"--load-extension={EXTENSION_PATH}",
                    f"--headless=new"
                ],
                user_agent=gen_ua
            )
            self.browser = browser
            print(self.extension_id, type(self.extension_id))

            if not self.extension_id:
                self.extension_id = await self.take_extension_id()

            page = await browser.new_page()

            await page.goto(f"chrome-extension://{self.extension_id}/popup.html")
            await asyncio.sleep(10_000)

    async def _initialize_browser(self):
        p = await async_playwright().start()
        self.browser = await p.chromium.launch_persistent_context(
            user_data_dir=SESSION_PATH / f"{self.mail.split('@')[0]}",
            channel="chrome",
            headless=True,
            no_viewport=False,
            proxy=self.proxy,
            args=[
                f"--disable-extensions-except={EXTENSION_PATH}",
                f"--load-extension={EXTENSION_PATH}",
                f"--headless=new"
            ],
            user_agent=gen_ua
        )

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
            self.browser = None

    # async def login(self):
    #     if self.browser:
