import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import base64
import codecs

class SendEmail:
    def __init__(self,pwd_path,EMAIL_REPORT_FROM_ADDRESS,EMAIL_REPORT_SMTP_SERVER,SMTP_SERVER_PORT):
        '''
        :param pwd_path: encode_smtp_pwd file
        :param EMAIL_REPORT_FROM_ADDRESS
        '''
        self.pwd_path = pwd_path # encode_smtp_pwd file
        self.EMAIL_REPORT_FROM_ADDRESS = EMAIL_REPORT_FROM_ADDRESS
        self.EMAIL_REPORT_SMTP_SERVER = EMAIL_REPORT_SMTP_SERVER
        self.SMTP_SERVER_PORT = SMTP_SERVER_PORT #587


    def test_encode_smtp_pwd(self,ori_password):
        encoded = codecs.encode(str(base64.b64encode(bytes(ori_password, encoding='utf-8')), encoding="utf-8"), 'rot_13')
        print(encoded)
        return (encoded)


    def test_decode_smtp_pwd(self,encoded_password):
        decoded = base64.b64decode(codecs.decode(encoded_password, 'rot_13')).decode('utf-8')
        print(decoded)


    def _decode_smtp_pwd(self):
        with open(self.pwd_path) as f:
            pwd = f.readline()
        decoded = base64.b64decode(codecs.decode(pwd, 'rot_13')).decode('utf-8')
        return decoded


    def send_email(self,subject, html_content,mailto_string, mailcc_string, attach_file=''):
        mailto_list = mailto_string.split(';')
        mailcc_list = mailcc_string.split(';')
        smtp_password = self._decode_smtp_pwd()
        message = MIMEMultipart()
        message['Subject'] = Header(subject)
        message['From'] = self.EMAIL_REPORT_FROM_ADDRESS
        message['To'] = ', '.join(mailto_list)
        message['Cc'] = ', '.join(mailcc_list)
        message.attach(MIMEText(html_content, 'html', 'utf-8'))

        if attach_file != '':
            # attachment
            with open(attach_file, "rb") as f:
                part = MIMEApplication(
                    f.read(),
                    Name=basename(attach_file)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="build.%s"' % basename(attach_file)
            message.attach(part)

        # Login and Send
        smtp = smtplib.SMTP(self.EMAIL_REPORT_SMTP_SERVER, self.SMTP_SERVER_PORT)
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self.EMAIL_REPORT_FROM_ADDRESS, smtp_password)
            smtp.sendmail(message['From'], mailto_list + mailcc_list, message.as_string())
        except Exception as e:
            print(e)
            return -1


if __name__ == '__main__':
    pass




