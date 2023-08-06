def send_message(resource, user_id, message):
    """Send email via Gmail API

    :param resource: Gmail API Resource
    :param user_id: sender Gmail API userId
    :param message: email.mime.multipart.MIMEMultipart
    :return: Gmail API response
    """
    message = resource.users().messages().send(
        userId=user_id,
        body=message
    ).execute()
    return message

