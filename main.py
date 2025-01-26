import asyncio
from core.AlphaOS import AlphaOS
import csv
from data.config import CONFIG_DIR


def parse_accounts_data():
    accounts = []
    with open(CONFIG_DIR / 'accounts.csv', 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            accounts.append(row)
    return accounts


async def action_user(data: list):
    while True:
        tasks = []
        a = input("Select number:\n1. Login accounts\n2. Start automate\n3. Auto farm cookies\n").strip()
        if a == "1":
            for r in data:
                tasks.append(asyncio.create_task(
                    AlphaOS(id=r['id'], mail=r['mail'], proxy=r['proxy']).create_profile_and_login()))
        elif a == "2":
            for s in data:
                tasks.append(asyncio.create_task(AlphaOS(id=s['id'], mail=s['mail'], proxy=s['proxy']).work()))
        elif a == "3":
            for f in data:
                tasks.append(asyncio.create_task(AlphaOS(id=f['id'], mail=f['mail'], proxy=f['proxy']).farm_cookies()))
        else:
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
