def delete_message(resource, user_id, message_id):
    """Send email via Gmail API

    :param resource: Gmail API Resource
    :param user_id: message_id owner Gmail API userId
    :param message_id: Gmail API message_id id
    :return: Gmail API response
    """
    response = resource.users().messages().delete(
        userId=user_id,
        id=message_id
    ).execute()
    return response


def batch_delete(resource, user_id, message_ids):
    """Batch delete a list of Gmail messages

    :param resource: Gmail API Resource
    :param user_id: message_id owner Gmail API userId
    :param message_ids: list, dict, Gmail message_id objects
    :return: dict, Gmail API response
    """
    payload = {"ids": [msg['id'] for msg in message_ids]}
    response = resource.users().messages().batchDelete(
        userId=user_id,
        body=payload
    ).execute()
    return response
