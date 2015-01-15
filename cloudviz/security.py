"""
Security implementation and configuration
"""

from pyramid.security import Allow, Everyone


class RootFactory(object):
    """
    Default ACLs
    """
    __acl__ = [
        (Allow, Everyone, 'public'),
        (Allow, 'group:apps', 'appauth'),
        (Allow, 'group:users', 'userauth')]

    def __init__(self, request):
        """
        Dummy constructor
        """
        pass


def appauth(_userid, _request):
    """
    Every user is an app user.
    Normally this function would map usernames to their corresponding
    group memberships. In our case, every user who passes who authentication
    is automatically a group:apps user.

    If we add cookie authentication in the future it will not use
    this callback function.
    """
    return ['group:apps']
