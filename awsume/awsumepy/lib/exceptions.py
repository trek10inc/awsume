class ProfileNotFoundError(Exception):
    """"""
    def __init__(self, profile_name='', message=''):
        self.profile_name = profile_name
        self.message = message
    def __str__(self):
        if self.message:
            return self.message
        return 'Profile {} not found.'.format(self.profile_name)


class InvalidProfileError(Exception):
    """"""
    def __init__(self, profile_name, message=''):
        self.profile_name = profile_name
        self.message = message
    def __str__(self):
        return 'Invalid profile {} {}'.format(self.profile_name, self.message)


class UserAuthenticationError(Exception):
    """"""
    def __init__(self, message=''):
        self.message = message
    def __str__(self):
        return self.message if self.message else 'Unable to get session token'


class RoleAuthenticationError(Exception):
    """"""
    def __init__(self, message=''):
        self.message = message
    def __str__(self):
        return self.message if self.message else 'Unable to assume role'
