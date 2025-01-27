import asyncio

from data.config import *
import csv


def parse_accounts_data():
    accounts = []
    with open(CONFIG_DIR / 'accounts.csv', 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            accounts.append(row)
    return accounts


async def save_ex_id(extension_id: str, user_id: str):
    rows = []
    with open(CONFIG_DIR / 'accounts.csv', 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            if row['id'] == user_id:
                row['extension_id'] = extension_id
            rows.append(row)

    with open(CONFIG_DIR / 'accounts.csv', "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "mail", "proxy", "extension_id"], delimiter=";")
        writer.writeheader()
        writer.writerows(rows)



