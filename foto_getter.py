# First Party Imports #
import imaplib
import email
import traceback
import os
import errno
from pathlib import Path

# Third Party Imports #
import configparser

config = configparser.ConfigParser(interpolation=None)
config.sections()
config.read(['.env', 'config'])
email_config = config['EMAIL']

ORG_EMAIL = "{}".format(email_config.get('emailDomain'))
FROM_EMAIL = "{0}{1}".format(email_config.get('emailHandle'), email_config.get('emailDomain'))
FROM_PWD = "{}".format(email_config.get('emailPassword'))
SMTP_SERVER = "{}".format(email_config.get('smtpServer'))
SMTP_PORT = int(email_config.get('smtpPort'))

# Save the attachment
def save_attachment(part):
  image_dir = config['DEFAULT'].get("imageDir")
  full_path = '{}{}'.format(image_dir, part.get_filename())

  # Create directory if it does not exist
  if not Path(image_dir).is_dir():
    try:
      os.makedirs(os.path.dirname(image_dir))
    except OSError as exc:  # Guard against race condition
      if exc.errno != errno.EEXIST:
        raise

  # Check if file exists before write
  if not Path(full_path).exists():
    with open(full_path, 'wb') as file_handle:
      file_handle.write(part.get_payload(decode=1))
      file_handle.close()

# Check if the attachment is a jpg
def check_attachment(fileName, contentType):
  if fileName is None:
    return False

  return fileName.endswith('.jpg') and contentType == 'image/jpeg'

# Read email from the provider
def read_email():
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
  except Exception as ex:
    traceback.print_exc()
    print(str(ex))

if __name__ == '__main__':
  read_email()
