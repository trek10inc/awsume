from awsume.awsumepy.lib import exceptions


def test_profile_not_found_error():
    err = exceptions.ProfileNotFoundError(profile_name='admin')
    assert str(err) == 'Profile admin not found.'


def test_profile_not_found_error_prioritize_message():
    err = exceptions.ProfileNotFoundError(profile_name='admin', message='You should see this only')
    assert str(err) == 'You should see this only'


def test_invalid_profile_error():
    err = exceptions.InvalidProfileError('admin', 'it is wack')
    assert str(err) == 'Invalid profile [admin] it is wack'


def test_user_authentication_error():
    err = exceptions.UserAuthenticationError()
    assert str(err) == 'Unable to get session token'


def test_user_authentication_error_message():
    err = exceptions.UserAuthenticationError('It did not work')
    assert str(err) == 'It did not work'


def test_role_authentication_error():
    err = exceptions.RoleAuthenticationError()
    assert str(err) == 'Unable to assume role'


def test_role_authentication_error_message():
    err = exceptions.RoleAuthenticationError('It did not work')
    assert str(err) == 'It did not work'
