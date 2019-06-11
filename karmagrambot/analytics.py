import dataset

from .config import DB_URI


def average_message_length(user_id, chat_id):
    db = dataset.connect(DB_URI)
    messages = db['messages'].find(user_id=user_id, chat_id=chat_id)
    messages = [m for m in messages if m['length'] is not None]

    if not messages:
        return 0

    return sum(m['length'] for m in messages) / len(messages)

def get_karma(user_id: int, chat_id: int) -> int:
    """Get the karma of an given user in a given chat.

    Args:
        user_id: The id of the user that we want to get the karma.
        chat_id: The id of the chat we're interested in.

    Returns:
        The karma value.
    """

    db = dataset.connect(DB_URI)
    user_messages = db['messages'].find(user_id=user_id, chat_id=chat_id)

    good_karma = 0
    bad_karma = 0
    for message in user_messages:
        replies_to_message = db['messages'].find(replied=message['message_id'])
        for reply in replies_to_message:
            if reply['vote'] == '+':
                good_karma += 1
            elif reply['vote'] == '-':
                bad_karma += 1

    return good_karma - bad_karma

def get_top_10_karmas(chat_id: int) -> list:
    """Get the top 10 karmas in a given group, if the doesn't have enough users, return the total amount.

    Args:
        chat_id: The id of the chat that we're interested in.

    Returns:
        A list with top 10 users with better karma.
    """

    db = dataset.connect(DB_URI)
    users = db['tracked'].find(chat_id=chat_id)
    users_id = [u['user_id'] for u in users]

    user_karma = {user_id: get_karma(user_id, chat_id) for user_id in users_id}

    sorted_users_id = sorted(user_karma, key=user_karma.get, reverse=True)

    sorted_users = []
    for i in range(len(sorted_users_id)):
        user_id = sorted_users_id[i]
        user = db['users'].find(user_id=user_id)

        for u in user:
            name = u['first_name']

            if u['last_name'] is not None:
                name += f" {u['last_name']}"

        sorted_users.append({'name': name, 'karma': user_karma[user_id]})


    top_10 = sorted_users[:10]

    return top_10
