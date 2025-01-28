import asyncio
import random
from typing import Optional
from utils.exeptions_os import *
from utils.data_change import *
from patchright.async_api import *
from patchright.sync_api import *
from data.config import *
import sys

sys.stdout.reconfigure(encoding='utf-8')


def try_parse_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


class AlphaOS:
    def __init__(self, id: str, mail: str, proxy: str, extension_id: str, user_agent: str):
        self.id = id
        self.mail = mail
        self.proxy = {
            'server': f'http://{proxy.split(":")[0]}:{proxy.split("@")[0].split(":")[1]}',
            'username': f'{proxy.split("@")[1].split(":")[0]}',
            'password': f'{proxy.split("@")[1].split(":")[1]}',
        }
        self.browser: Optional[Browser] = None
        self.extension_id = extension_id
        self.user_agent = user_agent
        logger.info(f"Account: {self.mail} init")

    async def _check_data(self):
        if not self.browser:
            await self._initialize_browser()

        if not self.user_agent:
            self.user_agent = ua.random
            await save_ua(user_id=self.id, ua=self.user_agent)

        if not self.extension_id:
            self.extension_id = await self.take_extension_id()

    async def farm_cookies(self):
        try:
            logger.info(f"Account: {self.mail} Cookie farm start.")
            await self._initialize_browser()
            selected_sites = random.sample(SITES_FARM_COOKIES, random.randint(5, len(SITES_FARM_COOKIES)))

            for site in selected_sites:
                await self._visit_site(site)
            await self.browser.close()
            logger.info(f"Account: {self.mail} Cookie farm is finished.")
        except KeyboardInterrupt:
            await self._close_browser()
        except Exception as ex:
            print(ex)
            logger.error(f"Account: {self.mail} Ex: {ex}")
        finally:
            await self._close_browser()

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
        except KeyboardInterrupt:
            await self._close_browser()
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
            logger.info(f"Account: {self.mail} get extension - {extension}")
            return extension
        except PermissionError as ex:
            logger.error(f"Account: {self.mail} {ex}")
        except KeyboardInterrupt:
            await self._close_browser()
        except Exception as ex:
            logger.error(f"Account: {self.mail} {ex}")

    async def work(self):
        try:
            not_found_sleep = NOT_FOUND_SLEEP_START

            while True:
                try:
                    print("Check data")
                    await self._check_data()

                    await self.browser.new_page()
                    page = await self.browser.new_page()

                    async with (page.expect_response(
                            lambda response: "api.alphaos.net/apis/users/profile" in response.url and response.request.method == 'GET') as
                    response_info):
                        await page.goto(f'chrome-extension://{self.extension_id}/popup.html', timeout=60_000)
                        logger.info(f'{self.mail} Load popup')
                        print(f'{self.mail} Load popup')
                        await page.wait_for_load_state('load', timeout=60_000)

                    response_profile = await response_info.value

                    if response_profile.status == 200:
                        print(f"Account: {self.mail} logined")
                        pass
                    elif response_profile.status == 401:
                        logger.error(f"Account: {self.mail} check login. click btn login..")
                        print(f"Account: {self.mail} check login. click btn login..")

                        await page.locator('xpath=//*[@id="__plasmo"]/span/span/div/div[1]/div[1]/div[1]').click(
                            timeout=60_000)
                        print("Click img")

                        await page.wait_for_load_state('load')

                        # await self.user_is_login()
                        if await self.user_is_login(page):
                            print(f"Account: {self.mail} site back 200. try again")
                            await page.close()
                            continue
                        else:
                            print(f"Account: {self.mail} need relogin.")
                            raise UnauthorizedError
                    else:
                        logger.error(
                            f"Account: {self.mail} back code: {response_profile.status} data: {response_profile.json()}")
                        print(
                            f"Account: {self.mail} back code: {response_profile.status} data: {response_profile.json()}")

                    # await page.goto(f'chrome-extension://{self.extension_id}/popup.html', timeout=60_000)

                    # await asyncio.sleep(random.randint(5, 10))
                    # await page.locator('xpath=//*[@id="__plasmo"]/span/span/div/div[1]/div[1]/div[1]').click(
                    #     timeout=60_000)
                    # logger.info(f'{self.mail} Load mining page')
                    # print(f'{self.mail} Load mining page')
                    await page.locator('xpath=//*[@id="__plasmo"]/span/span/div/div[1]/div[1]/div[1]').click(
                        timeout=60_000)
                    print("Click img")

                    await page.wait_for_load_state('load', timeout=60_000)
                    await asyncio.sleep(random.randint(1, 3))

                    button_start_mining = page.locator('button', has_text='Start Mining')
                    button_stop_mining = page.locator('button', has_text='Stop Mining')

                    if await button_start_mining.count() > 0:
                        await asyncio.sleep(3)
                        await button_start_mining.click(timeout=60_000)
                        logger.info(f"Account: {self.mail} Start mining.")
                        print(f"Account: {self.mail} Start mining.")

                        # if await page.locator('h2', has_text='Automated Mining').first.is_visible(timeout=60_000):
                        #     await page.locator('xpath=//*[@id="content-:rt:"]/span[3]/button').click(timeout=60_000)

                    elif await button_stop_mining.count() > 0:
                        logger.info(f"Account: {self.mail} Mining is already in progress.")
                    else:
                        logger.error(
                            f"Account: {self.mail} Buttons start/stop not found. Sleep delay: {not_found_sleep}")
                        print(f"Account: {self.mail} Buttons start/stop not found. Sleep delay: {not_found_sleep}")
                        await asyncio.sleep(not_found_sleep)
                        not_found_sleep *= 2
                        continue

                    mining_points = await page.locator(
                        'xpath=//*[@id="__plasmo"]/span/span/div/div[2]/div/div[2]/span[1]/span').inner_text(
                        timeout=60_000)
                    total_balance = await page.locator(
                        '//*[@id="__plasmo"]/span/span/div/div[2]/div/div[1]/span[2]').inner_text(timeout=60_000)

                    time_sleep_interval = random.randint(ACCOUNT_CHECK_INTERVAL[0], ACCOUNT_CHECK_INTERVAL[1])
                    logger.info(
                        f"Account: {self.mail} | Ready to claim: {mining_points} | Total balance: {total_balance} | Sleep: {time_sleep_interval} sec.")
                    print(
                        f"Account: {self.mail} | Ready to claim: {mining_points} | Total balance: {total_balance} | Sleep: {time_sleep_interval} sec.")
                    if try_parse_int(mining_points) > 10:
                        await page.locator('button', has_text='Claim').click(timeout=60_000)
                        logger.info(f'Account: {self.mail} | Claim click.')
                        print(f'Account: {self.mail} | Claim click.')

                    await asyncio.sleep(time_sleep_interval)
                except UnauthorizedError:
                    logger.error(f"Account: {self.mail} is not authorized! Account discconected")
                    print(f"Account: {self.mail} is not authorized! Account discconected")
                    await self.browser.close()
                    return
                except TimeoutError as e:
                    logger.error(f"Account: {self.mail} not found item. Try again... \n{e}")
                    print(f"Account: {self.mail} not found item. Try again... \n{e}")
                    await asyncio.sleep(not_found_sleep)
                    not_found_sleep *= 2
                    continue
        except KeyboardInterrupt:
            await self._close_browser()

    async def user_is_login(self, page):
        try:
            print(f"Account: {self.mail} loading site...")

            # input()

            async with page.expect_response(
                    lambda response: "api.kekkai.io/apis/users/profile" in response.url and response.request.method == 'GET',
                    timeout=30_000) as response_info:
                await page.goto(f"https://alphaos.net/point")

            input()
            response = await response_info.value

            if response.status == 200:
                return True
            elif response.status == 401:
                return False
            else:
                data = await response.json()
                print(f"Account: {self.mail} profile returned {response.status} {data}")
                return False
        except TimeoutError:
            print(f"Account: {self.mail} request timed out. Skipping...")
            return False
        except KeyboardInterrupt:
            await self._close_browser()
        except Exception as e:
            print(f"Account: {self.mail} encountered an error: {e}")
            return False

    async def login_account(self):
        while True:
            try:
                await self._check_data()
                page = await self.browser.new_page()

                if await self.user_is_login(page):
                    logger.info(f"Account: {self.mail} user is login")
                    print(f"Account: {self.mail} user is login!")
                    return
                else:
                    logger.info(f"Account: {self.mail} user is not login..")
                    print(f"Account: {self.mail} user is not login..")

                await page.wait_for_load_state('load')
                print(f'Account: {self.mail} page is load')
                logger.info(f'Account: {self.mail} page is load')

                await page.reload(timeout=60_000)
                print(f"Account: {self.mail} page reload")
                logger.info(f"Account: {self.mail} page reload")

                await page.wait_for_load_state('load')
                await page.locator('xpath=//span[contains(text(), "JOIN NOW")]').first.click(timeout=60_000)

                print(f"Account: {self.mail} click btn JOIN NOW")
                logger.info(f"Account: {self.mail} click btn JOIN NOW")

                # await page.locator(
                #     'xpath=/html/body/div[1]/div[4]/div/div[1]/div/span/div/div/div[2]/div/div[1]/div[1]/div[1]/div[2]/div[1]').click(
                #     timeout=60_000)
                # print("click")
                # await asyncio.sleep(2)
                # await page.locator('xpath=//*[@id="content-:r7g:"]/div/div/div/span[6]/button/span/span/button').click(
                #     timeout=60_000)

                # await page.wait_for_selector('input[placeholder="Please enter email to continue"]')
                print(f"Account: {self.mail} enter email..")
                await asyncio.sleep(3)
                input_mail = page.locator(
                    'input[placeholder="Please enter email to continue"]')

                await input_mail.click(timeout=60_000)
                await page.keyboard.type(self.mail, delay=300)

                if await page.locator('span', has_text='Invalid Address').first.is_visible(timeout=60_000):
                    logger.error(f"Account: {self.mail} incorrect mail.")
                    print(f"Account: {self.mail} incorrect mail.")
                    exit()

                await page.locator(
                    "xpath=/html/body/div[1]/div[4]/div/div[2]/div/div[3]/div/div[3]/span/span/button").click(
                    timeout=60_000)
                print(f"Account: {self.mail} click next..")

                await page.locator('xpath=//*[@id="content-:ra5:"]/div/span[2]/span/button').click(
                    timeout=60_000)  # https://api.kekkai.io/apis/users/sign-in
                print(f"Account: {self.mail} agree..")

                await page.locator('span', has_text='Enter Verification Code to continue').first.is_visible(
                    timeout=60_000)
                print(f"Account: {self.mail} message send..")

                while True:
                    code = input(f"Account: {self.mail} enter code: ").strip()
                    async with (page.expect_response(
                            lambda response: "api.kekkai.io/apis/users/sign-in" in response.url and response.request.method == 'POST') as response_sign_in):
                        await page.fill('xpath=/html/body/div[1]/div[4]/div/div[3]/div/div[3]/div/div/input', code)

                    response_sign_in = await response_sign_in.value
                    if response_sign_in.status == 201:
                        print(f"Account: {self.mail} successful login. sleep 20 seconds for save cookie")
                        await asyncio.sleep(20)
                        return
                    else:
                        print(f"Account: {self.mail} response status: {response_sign_in.status}. Try again")
                        continue
            except TimeoutError as e:
                logger.error(f"Account: {self.mail} {e} try again..")
                print(f"Account: {self.mail} {e} try again..")
                continue
            except KeyboardInterrupt:
                await self._close_browser()
            except Exception as ex:
                logger.error(ex)
                print(ex)
            finally:
                await self._close_browser()

    async def _initialize_browser(self):
        p = await async_playwright().start()
        self.browser = await p.chromium.launch_persistent_context(
            user_data_dir=SESSION_PATH / f"{self.mail.split('@')[0]}",
            channel="chrome",
            headless=False,
            no_viewport=False,
            proxy=self.proxy,
            args=[
                f"--disable-extensions-except={EXTENSION_PATH}",
                f"--load-extension={EXTENSION_PATH}",
                # f"--headless=new"
            ],
            user_agent=self.user_agent
        )
        logger.info(f"Account: {self.mail} browser create")
        print(f"Account: {self.mail} browser create")

    async def _close_browser(self):
        if self.browser:
            await self.browser.close()
            self.browser = None
            logger.info(f"Account: {self.mail} browser closed.")
            print(f"Account: {self.mail} browser closed.")
