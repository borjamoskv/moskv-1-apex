import smtplib
import sys

domain = "loading.es"
mx_record = "mx1.loading.es"
target_email = "silvia.m@gnetico.es"
from_email = "admin@gnetico.es"

try:
    server = smtplib.SMTP(mx_record, 25, timeout=10)
    server.set_debuglevel(0)
    server.helo("mail.loading.es")
    server.mail(from_email)
    code, message = server.rcpt(target_email)
    server.quit()
    print(f"SMTP CODE: {code}")
    print(f"MESSAGE: {message.decode('utf-8')}")
except Exception as e:
    print(f"ERROR: {e}")
