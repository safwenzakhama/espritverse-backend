# social/utils.py
from accounts.models import FriendRequest

def get_friend_ids(user_id: int) -> set[int]:
    """
    Returns a set of user IDs who are 'friends' with the given user.
    Friendship is defined as FriendRequest with status=ACCEPTED in either direction.
    """
    qs = FriendRequest.objects.filter(status=FriendRequest.ACCEPTED).values_list("sender_id", "receiver_id")
    friends = set()
    for s, r in qs:
        if s == user_id:
            friends.add(r)
        elif r == user_id:
            friends.add(s)
    return friends
