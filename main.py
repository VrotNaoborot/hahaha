import asyncio
from core.AlphaOS import AlphaOS
import csv
from data.config import CONFIG_DIR
from utils.data_change import *

import os
import shutil
import asyncio


async def action_user(data: list):
    while True:
        tasks = []
        a = input(
            "Select number:\n1. Login accounts\n2. Start automate\n3. Auto farm cookies\n4. Clear sessions\n5. Break\n").strip()

        if a == "1":
            # Очистка папки sessions перед логином
            if os.path.exists("sessions"):
                shutil.rmtree("sessions")
                os.makedirs("sessions")
            for r in data:
                await AlphaOS(id=r['id'], mail=r['mail'], proxy=r['proxy'], extension_id=r.get('extension_id', None),
                              user_agent=r['user_agent']).login_account()
        elif a == "2":
            for s in data:
                tasks.append(asyncio.create_task(AlphaOS(id=s['id'], mail=s['mail'], proxy=s['proxy'],
                                                         extension_id=s.get('extension_id', None),
                                                         user_agent=s['user_agent']).work()))
        elif a == "3":
            for f in data:
                tasks.append(asyncio.create_task(AlphaOS(id=f['id'], mail=f['mail'], proxy=f['proxy'],
                                                         extension_id=f.get('extension_id', None),
                                                         user_agent=f['user_agent']).farm_cookies()))
        elif a == "4":
            # Очистка папки sessions
            if os.path.exists(SESSION_PATH):
                shutil.rmtree(SESSION_PATH)
                os.makedirs(SESSION_PATH)
                print("Sessions cleared.")
            else:
                print("Sessions folder does not exist.")
            continue
        elif a == '5':
            break

        else:
            print(f"Incorrect value.")
            continue

        await asyncio.gather(*tasks)


async def main():
    data = parse_accounts_data()
    if not data:
        print(f"accounts.csv is empty")
        exit()
    await action_user(data)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
