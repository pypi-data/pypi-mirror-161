import smtplib, email, imaplib, mailbox, datetime
from email.header import decode_header
class Email:
    def send_gmail(password, senderEmail, receiverEmail, message):
        """
        This function sends an email to the email address given.
        Only 2,000 messages can be sent per day.
        Some emails may not be sent if it's an suspicious email.
        """
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(senderEmail, password)
        server.sendmail(senderEmail, receiverEmail, message)
        server.quit()
    def send_outlook_email(password, senderEmail, receiverEmail, message):
        """
        This function sends an email to the email address given.
        """
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.starttls()
        server.login(senderEmail, password)
        server.sendmail(senderEmail, receiverEmail, message)
        server.quit()
    def send_office365_email(password, senderEmail, receiverEmail, message):
        """
        This function sends an email to the email address given.
        """
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(senderEmail, password)
        server.sendmail(senderEmail, receiverEmail, message)
        server.quit()