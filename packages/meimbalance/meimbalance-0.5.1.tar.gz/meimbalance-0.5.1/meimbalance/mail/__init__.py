
# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from meimbalance import sqllog 

def send_mail(recipient: str, subject: str, msg_content: str, sender: str='noreply-kraftforvaltning@ae.no'):
	message = Mail(
		from_email=sender,
		to_emails=recipient,
		subject=subject,
		html_content=msg_content)
	try:
		sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
		response = sg.send(message)
		sqllog.log_application('INFO', 'Mail with subject ' + subject + ' sent to ' + recipient, 'meimbalance.mail')
		sqllog.log_application('DEBUG', str(response.headers), 'meimbalance.mail')
	except Exception as e:
		sqllog.log_application('ERROR', str(e.message), 'meimbalance.mail')