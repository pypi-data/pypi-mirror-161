import inspect


def get_labels(resource, user_id):
    """Get a list of message labels for user_id
    
    :param resource: Gmail API Resource
    :param user_id: sender Gmail API userId
    :return: Gmail API response
    """
    response = resource.users().labels().list(
        userId=user_id
    ).execute()
    return response


def add_labels(resource, user_id, message_id, labels):
    """Apply a list of labels to a Gmail message

    :param resource: Gmail API resource
    :param user_id: str, Gmail API userId
    :param message_id: str, Gmail message id
    :param labels: list, str, labels to apply to message
    :return: Gmail API response
    """
    if not type(labels) is list:
        raise ValueError(
            f'{inspect.stack()[0][3]} requires list for labels arg'
        )
    response = resource.users().messages().modify(
        userId=user_id,
        id=message_id,
        body={'addLabelIds': labels}
    ).execute()
    return response


def get_label_by_name(resource, user_id, name):
    """Case insensitive search for a label by name

    :param resource: Gmail API Resource
    :param user_id: str, Gmail API userId
    :param name: str, name of label to try to get
    :return: Gmail label object or None
    """
    labels = get_labels(resource, user_id)
    for label in labels['labels']:
        if label['name'].lower() == name.lower():
            return label
    else:
        return None


def remove_labels(resource, user_id, message_id, labels):
    """Remove a list of labels from a Gmail message

    :param resource: Gmail API resource
    :param user_id: str, Gmail API userId
    :param message_id: str, Gmail message id
    :param labels: list, str, list of label ids to remove
    :return: Gmail API response
    """
    if not type(labels) is list:
        raise ValueError(
            f'{inspect.stack()[0][3]} requires list for labels arg'
        )
    response = resource.users().messages().modify(
        userId=user_id,
        id=message_id,
        body={'removeLabelIds': labels}
    ).execute()
    return response
