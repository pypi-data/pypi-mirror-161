from email.message import EmailMessage
import ssl
import smtplib
import imghdr
import pylejandria


def send_email(
    from_: str, password: str, to_: str, subject: str, content: str,
    files: list[str] | None=[]
) -> None:
    """
    Sends an email with the given subject, content and optional files.

    Args:
        from_ (str): sender email.
        password (str): password of the sender email.
        to_ (str): receiver email.
        subject (str): subject of the email.
        content (str): content of the email.
        files (list[str], optional): list of paths of files to attach to the
        email. Defaults to [].
    """
    mail = EmailMessage()
    mail['From'] = from_
    mail['To'] = to_
    mail['Subject'] = subject
    mail.set_content(content)

    for f in files:
        with open(f, 'rb') as file:
            file_data = file.read()
            file_name = file.name
            file_type = imghdr.what(file_name)
        mail.add_attachment(
            file_data, filename=file_name, subtype=file_type, maintype=''
        )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(from_, password)
        smtp.sendmail(from_, to_, mail.as_string())

if __name__ == '__main__':
    send_email(
        'pylejandria@gmail.com', 'feywinwpqwhjnwzz',
        'angelshaparro@outlook.com', 'PyLejandria mail', 'jajaja contexto',
        files=pylejandria.gui.ask('openfilenames')
    )
