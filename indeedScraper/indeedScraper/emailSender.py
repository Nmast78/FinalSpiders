import smtplib

from email.message import EmailMessage

# Sends an email if any of the fields are null
# NEED TO CONFIGURE THIS WITH A NEW GMAIL ACCOUNT
def send_email(field):
    msg = EmailMessage()
    msg.set_content("There has been an error in the Indeed Spider\n" + str(field))

    msg['Subject'] = "Indeed script failing"
    msg['From'] = ""
    msg['To'] = ""

    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

if __name__ == "__main__":
    send_email("Test")