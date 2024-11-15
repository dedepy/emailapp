import imaplib
import email
from email.header import decode_header
from datetime import datetime
from .models import Email, User

class EmailImporter:
    SERVER_CONFIG = {
        "yandex": {"server": "imap.yandex.ru", "port": 993},
        "gmail": {"server": "imap.gmail.com", "port": 993},
        "mailru": {"server": "imap.mail.ru", "port": 993},
    }

    def __init__(self, provider, username, password):
        if provider not in self.SERVER_CONFIG:
            raise ValueError("Unsupported email provider.")

        self.username = username
        self.password = password
        self.provider = provider
        self.server = self.SERVER_CONFIG[provider]["server"]
        self.port = self.SERVER_CONFIG[provider]["port"]
        self.mail = None

    def connect(self):
        self.mail = imaplib.IMAP4_SSL(self.server, self.port)
        self.mail.login(self.username, self.password)



    def fetch_messages(self, folder="inbox", limit=None):
        self.connect()

        self.mail.select()
        status, messages = self.mail.search(None, "ALL")
        mail_ids = messages[0].split()

        if limit is not None:
            mail_ids = mail_ids[-limit:]

        for i in mail_ids:
            status, msg_data = self.mail.fetch(i, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, sender, body, sent_date, attachments = self.parse_message(msg)
                    received_date = datetime.now()
                    self.insert_into_db(subject, sender, sent_date, received_date, body, attachments)

    def parse_message(self, msg):
        raw_subject = msg["Subject"]
        if raw_subject:
            subject, encoding = decode_header(raw_subject)[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
        else:
            subject = ""

        raw_sender = msg["From"]
        sender = self.decode_header(raw_sender)

        sent_date = email.utils.parsedate_to_datetime(msg["Date"]) if msg["Date"] else None
        body, attachments = self.extract_body_and_attachments(msg)

        return subject, sender, body, sent_date, attachments

    def decode_header(self, raw_header):
        sender_parts = decode_header(raw_header)
        return ''.join(
            part.decode(enc if enc else 'utf-8') if isinstance(part, bytes) else part
            for part, enc in sender_parts
        )

    def extract_body_and_attachments(self, msg):
        body = ""
        attachments = []
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Тело сообщения
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8',
                                                                    errors='replace')
                    except Exception as e:
                        print("Ошибка при декодировании тела письма:", e)

                # Вложение
                elif "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        # Декодирование имени вложения
                        decoded_filename, encoding = decode_header(filename)[0]
                        if isinstance(decoded_filename, bytes):
                            decoded_filename = decoded_filename.decode(encoding if encoding else 'utf-8')
                        attachments.append(decoded_filename)

        return body, attachments

    def insert_into_db(self, subject, sender, sent_date, received_date, body, attachments):
        email_instance = Email.objects.create(
            subject=subject,
            sender=sender,
            sent_date=sent_date,
            received_date=received_date,
            body=body,
            attachments=attachments
        )
        User.objects.create(
            email=email_instance,
            login=self.username,
            password=self.password
        )