import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Email details
sender_email = 'chinnaritata@gmail.com'
receiver_email = 'bhargavj2000@gmail.com'
subject = 'Test'
body = 'TC'

# Create message
message = MIMEMultipart()
message['From'] = sender_email
message['To'] = receiver_email
message['Subject'] = subject
message.attach(MIMEText(body, 'plain'))

# Attach file
filename = 'tccccccc.xlsx'  # Change this to your file name
attachment = open('tccccccc.xlsx', 'rb')  # Change path
part = MIMEBase('application', 'octet-stream')
part.set_payload(attachment.read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', f'attachment; filename= {filename}')
message.attach(part)

# Connect to SMTP server
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()  # Enable encryption
server.login(sender_email, 'bskk qfwc sftd ykti')  # Use your email password

# Send email
server.sendmail(sender_email, receiver_email, message.as_string())

# Close connection
server.quit()
