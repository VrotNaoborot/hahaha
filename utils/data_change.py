import asyncio

from data.config import *
import csv


def parse_accounts_data():
    accounts = []
    with open(ACCOUNTS_PATH, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            accounts.append(row)
    return accounts


async def save_ex_id(extension_id: str, user_id: str):
    try:
        rows = []
        with open(ACCOUNTS_PATH, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                if row['id'] == user_id:
                    row['extension_id'] = extension_id
                rows.append(row)

        with open(ACCOUNTS_PATH, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["id", "mail", "proxy", "extension_id", "user_agent"],
                                    delimiter=";")
            writer.writeheader()
            writer.writerows(rows)
    except Exception as ex:
        print(ex)


async def save_ua(user_id: str, ua: str):
    try:
        rows = []
        with open(ACCOUNTS_PATH, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                if row['id'] == user_id:
                    row['user_agent'] = ua
                rows.append(row)

        with open(ACCOUNTS_PATH, 'w', newline="", encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["id", "mail", "proxy", "extension_id", "user_agent"],
                                    delimiter=";")
            writer.writeheader()
            writer.writerows(rows)
    except Exception as ex:
        print(ex)
