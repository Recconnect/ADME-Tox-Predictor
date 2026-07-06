"""
Email Sender - SMTP клиент для Яндекс.Почты
Поддерживает Gmail, Яндекс.Почту, SendGrid
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class EmailSender:
    def __init__(self, username=None, password=None, smtp_host=None, smtp_port=465):
        self.username = username or os.getenv("EMAIL_USER")
        self.password = password or os.getenv("EMAIL_PASSWORD")
        self.smtp_host = smtp_host or self._detect_smtp_host(self.username)
        self.smtp_port = smtp_port

        if not self.username or not self.password:
            raise ValueError("EMAIL_USER and EMAIL_PASSWORD must be set in .env")

        self.db_path = Path(__file__).parent.parent / "data" / "email_log.db"
        self._init_db()

    def _detect_smtp_host(self, email):
        """Автоопределение SMTP сервера по домену"""
        if "@yandex" in email or "@cdo.ru" in email:
            return "smtp.yandex.ru"
        elif "@gmail.com" in email:
            return "smtp.gmail.com"
        elif "@mail.ru" in email:
            return "smtp.mail.ru"
        else:
            return "smtp.yandex.ru"  # default

    def _init_db(self):
        """Инициализация базы данных для логирования писем"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                to_email TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                sent_at REAL NOT NULL,
                status TEXT DEFAULT 'sent'
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_emails_sent_at ON emails(sent_at)
        """)
        conn.commit()
        conn.close()

    def send(self, to_email, subject, body, html=False):
        """Отправка email"""
        msg = MIMEMultipart()
        msg["From"] = self.username
        msg["To"] = to_email
        msg["Subject"] = subject

        content_type = "html" if html else "plain"
        msg.attach(MIMEText(body, content_type, "utf-8"))

        try:
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
                server.starttls()

            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()

            self._log_email(to_email, subject, body, "sent")
            return True
        except Exception as e:
            self._log_email(to_email, subject, body, f"failed: {e}")
            raise

    def _log_email(self, to_email, subject, body, status):
        """Логирование отправленного письма"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "INSERT INTO emails (to_email, subject, body, sent_at, status) VALUES (?, ?, ?, ?, ?)",
            (to_email, subject, body, datetime.now().timestamp(), status),
        )
        conn.commit()
        conn.close()

    def get_sent_count(self, days=7):
        """Количество отправленных писем за N дней"""
        conn = sqlite3.connect(str(self.db_path))
        cutoff = datetime.now().timestamp() - days * 86400
        count = conn.execute(
            "SELECT COUNT(*) FROM emails WHERE sent_at >= ? AND status = 'sent'",
            (cutoff,),
        ).fetchone()[0]
        conn.close()
        return count

    def get_daily_sent(self):
        """Количество писем, отправленных сегодня"""
        conn = sqlite3.connect(str(self.db_path))
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        count = conn.execute(
            "SELECT COUNT(*) FROM emails WHERE sent_at >= ? AND status = 'sent'",
            (today_start,),
        ).fetchone()[0]
        conn.close()
        return count
