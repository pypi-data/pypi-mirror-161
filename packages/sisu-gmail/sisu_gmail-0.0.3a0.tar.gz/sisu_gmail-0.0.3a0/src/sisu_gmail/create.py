import sisu_email.create


def encode_multipart_message(message):
    """Encode multipart message_id as urlsafe base64 string

    :param message: email.mime.multipart.MIMEMultipart
    :return: dict, {'raw': base64_string_of_message}
    """
    return {
        'raw': sisu_email.create.encode_multipart_message(message)
    }

