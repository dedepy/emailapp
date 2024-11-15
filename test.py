import imaplib

server = "imap.gmail.com"
port = 993
username = "loxcvadrat@gmail.com"
password = "xoww vvby shii vswq"

try:
    mail = imaplib.IMAP4_SSL(server, port)
    mail.login(username, password)
    print("Успешно подключились.")

    status, messages = mail.select("INBOX")
    print(f"Выбор папки INBOX: статус={status}, сообщения={messages}")
except imaplib.IMAP4.error as e:
    print(f"Ошибка: {e}")
