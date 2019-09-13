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


class SAMLAssertionNotFoundError(Exception):
    """"""
    def __init__(self, message=''):
        self.message = message
    def __str__(self):
        return self.message if self.message else 'No SAML assertion'


class SAMLAssertionMissingRoleError(Exception):
    """"""
    def __init__(self, message=''):
        self.message = message
    def __str__(self):
        return self.message if self.message else 'No role in the SAML assertion'


class SAMLRoleNotFoundError(Exception):
    """"""
    def __init__(self, role_arn, message=''):
        self.role_arn = role_arn
        self.message = message
    def __str__(self):
        return self.message if self.message else 'No match for SAML provider and role: {}'.format(self.role_arn)


class SAMLAssertionParseError(Exception):
    """"""
    def __init__(self, message=''):
        self.message = message
    def __str__(self):
        return self.message if self.message else 'Cannot parse SAML assertion'


class NoCredentialsError(Exception):
    """"""
    def __init__(self, message=''):
        self.message = message
    def __str__(self):
        return self.message if self.message else 'No credentials'
