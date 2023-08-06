QUERIES = {
    'FROM_ADDRESS': 'from:'
}


class NoNextPageToken(KeyError):
    pass


def next_page(resource, user_id, query, response, max_results=100):
    """Get next page of search results

    :param resource: Gmail API resource
    :param user_id: str, Gmail API userId
    :param query: str, Gmail API search query
    :param response: dict, Gmail API search query response
    :param max_results: int, number of results per request
    :return: list, dicts of gmail message_id message_ids and thread message_ids
    """
    if not type(response) is dict:
        raise TypeError(
            'next_search_page requires dict as response param'
        )
    elif 'nextPageToken' not in response:
        raise NoNextPageToken(
            'next_search_page requires dict with nextPageToken key'
        )

    page_token = response['nextPageToken']
    return resource.users().messages().list(
        userId=user_id,
        q=query,
        pageToken=page_token,
        maxResults=max_results
    ).execute()


def search(resource, user_id, query, max_results=100):
    """Return search results response for a Gmail API query

    :param resource: Gmail API resource
    :param user_id: str, Gmail API userId
    :param query: str, Gmail API search query
    :param max_results: int, number of results per request
    :return: Gmail API search response
    """
    return resource.users().messages().list(
        userId=user_id,
        q=query,
        maxResults=max_results
    ).execute()


def iter_messages(resource, user_id, query):
    """Generator to return search results

    :param resource: Gmail API resource
    :param user_id: str, Gmail API userId
    :param query: str, Gmail API search query
    :return: dict, gmail message_id message_ids and thread message_ids
    """
    response = resource.users().messages().list(
        userId=user_id,
        q=query
    ).execute()

    if 'messages' in response:
        part = response['messages']
        for index, result in enumerate(part, start=1):
            yield result
            if len(part) == index and 'nextPageToken' in response:
                next_page(resource, user_id, response, query)


def search_by_address(resource, user_id, address):
    """Search gmail for messages by sender email address

    :param resource: Gmail API Resource
    :param user_id: str, Gmail API userId
    :param address: str, Gmail address
    :return: list, dict of Gmail message ids and thread ids:
    """
    return search(
        resource,
        user_id,
        f"{QUERIES['FROM_ADDRESS']}{address}"
    )
