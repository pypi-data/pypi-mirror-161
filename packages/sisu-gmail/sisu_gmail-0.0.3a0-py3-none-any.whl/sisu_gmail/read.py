def download_message(resource, user_id, message_id):
    """Download a message by id

    :param resource: Gmail API Resource
    :param user_id: message_id owner Gmail API userId
    :param message_id: str, Gmail message id
    :return: dict of message contents
    """
    return resource.users().messages().get(
        userId=user_id,
        id=message_id
    ).execute()
