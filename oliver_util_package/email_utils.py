from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
# for attachments
from email.mime.base import MIMEBase
from email import encoders
# get file_name without directories
from os.path import basename
import datetime
# custom package
import io_utils

def file_attach(file_path):
    """
    For email file attachment

    :param file_path:
    :return:
    """
    # email attachment
    email_file = MIMEBase('application', 'octet-stream')
    with open(file_path, 'rb') as f:
        file_data = f.read()

    email_file.set_payload(file_data)
    encoders.encode_base64(email_file)

    file_name = basename(file_path)
    email_file.add_header('Content-Disposition', 'attachment', filename=file_name)
    return email_file


def send_mail(receiver, subject, contents, file_path):
    """
    To send email

    :param receiver:
    :param subject:
    :param contents:
    :param file_path:
    :return:
    """
    try:
        email_dict = io_utils.get_config_data("email")

        # email info
        msg = MIMEMultipart('alternative')

        # email contents
        contents = contents

        msg['FROM'] = email_dict['SMTP_USER']
        msg['TO'] = receiver
        msg['SUBJECT'] = subject

        text = MIMEText(contents)
        msg.attach(text)

        if file_path != 'FILE':
            msg.attach(file_attach(file_path))

        smtp = smtplib.SMTP_SSL(email_dict['SMTP_SERVER'], email_dict['SMTP_PORT'])
        print('Serv connection Success!')
        smtp.login(email_dict['SMTP_USER'], email_dict['SMTP_PASSWORD'])
        print('Login Success!')
        smtp.sendmail(email_dict['SMTP_USER'], receiver, msg.as_string(contents))
        print('Sending email Success!')
    except Exception as e:
        print(e)
        print('Error!!!')
        pass
    finally:
        smtp.close()
        print('Sending Email Done!')


# email sending test
"""
try:
    send_mail('lvsin@naver.com', '결제확인메일', 'ㅋㅋㅋㅋㅋ', 'FILE')
except Exception as e:
    print("Error : ", e)
    pass
"""