import imaplib
import email
from email.header import decode_header

# Учетные данные
username = "dimaodincov3334@gmail.com"
password = "2004Dima2004"

# Подключение к IMAP-серверу Gmail
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(username, password)

# Выбор папки "Входящие"
mail.select("inbox")

# Поиск всех писем в папке
status, messages = mail.search(None, "ALL")
email_ids = messages[0].split()

# Получение последнего письма
latest_email_id = email_ids[-1]

# Извлечение письма
status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
msg = email.message_from_bytes(msg_data[0][1])

# Декодирование заголовков
subject, encoding = decode_header(msg["Subject"])[0]
if isinstance(subject, bytes):
    subject = subject.decode(encoding if encoding else "utf-8")
from_ = msg.get("From")

print("Тема:", subject)
print("От:", from_)

# Извлечение тела письма
if msg.is_multipart():
    for part in msg.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition"))
        if "attachment" not in content_disposition:
            body = part.get_payload(decode=True).decode()
            print("Содержание:", body)
else:
    body = msg.get_payload(decode=True).decode()
    print("Содержание:", body)

# Закрытие соединения
mail.close()
mail.logout()
