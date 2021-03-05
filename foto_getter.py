# First Party Imports #
import imaplib
import email
import traceback
import os
import errno
from pathlib import Path
from foto_reconcile import reconcile

# Third Party Imports #
import configparser

config = configparser.ConfigParser(interpolation=None)
config.sections()
config.read(['.env', 'config'])
EMAIL_CONFIG = config['EMAIL']
IMAGE_DIR = config['DEFAULT'].get("imageDir")
SHOULD_RECONCILE = config['DEFAULT'].get("shouldReconcile")

ORG_EMAIL = "{}".format(EMAIL_CONFIG.get('emailDomain'))
FROM_EMAIL = "{0}{1}".format(EMAIL_CONFIG.get(
    'emailHandle'), EMAIL_CONFIG.get('emailDomain'))
FROM_PWD = "{}".format(EMAIL_CONFIG.get('emailPassword'))
SMTP_SERVER = "{}".format(EMAIL_CONFIG.get('smtpServer'))
SMTP_PORT = int(EMAIL_CONFIG.get('smtpPort'))


def save_attachment(part):
    full_path = '{}{}'.format(IMAGE_DIR, part.get_filename())

    # Create directory if it does not exist
    if not Path(IMAGE_DIR).is_dir():
        try:
            os.makedirs(os.path.dirname(IMAGE_DIR))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    # Check if file exists before write
    if not Path(full_path).exists():
        with open(full_path, 'wb') as file_handle:
            file_handle.write(part.get_payload(decode=1))
            file_handle.close()


def check_attachment(fileName, contentType):
    if fileName is None:
        return False

    return fileName.endswith('.jpg') and contentType == 'image/jpeg'


def read_email():
    files_saved = []
    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(FROM_EMAIL, FROM_PWD)
        mail.select('inbox', readonly=True)

        # Only return email that have subject "foto"
        data = mail.search(None, 'SUBJECT "foto"')
        mail_ids = data[1]
        id_list = mail_ids[0].split()
        for ids in id_list:
            i = int(ids)
            data = mail.fetch(str(i), '(RFC822)')
            for response_part in data:
                arr = response_part[0]
                if isinstance(arr, tuple):
                    msg = email.message_from_string(str(arr[1], 'utf-8'))
                    for part in msg.walk():
                        if check_attachment(part.get_filename(), part.get_content_type()):
                            save_attachment(part)
                            files_saved.append(part.get_filename())
    except Exception as ex:
        traceback.print_exc()
        print(str(ex))

    if files_saved and SHOULD_RECONCILE:
        reconcile(files_saved)


if __name__ == '__main__':
    read_email()
