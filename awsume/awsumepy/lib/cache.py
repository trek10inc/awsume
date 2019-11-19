import os
import json
import dateutil
from datetime import datetime

from . import constants
from . logger import logger


def ensure_cache_dir():
    cache_dir = str(constants.AWSUME_CACHE_DIR)
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    os.chmod(cache_dir, 0o700) #ensure directory is secure.


def read_aws_cache(cache_file_name: str) -> dict:
    ensure_cache_dir()
    cache_path = str(constants.AWSUME_CACHE_DIR) + '/' + cache_file_name
    logger.debug('Cache file path: ' + cache_path)
    session = {}
    if os.path.isfile(cache_path):
        logger.debug('Cache file found')
        try:
            session = json.load(open(cache_path))
            if session.get('Expiration') and type(session.get('Expiration')) == str:
                session['Expiration'] = datetime.strptime(session['Expiration'], '%Y-%m-%d %H:%M:%S')
        except:
            logger.debug('There was an error reading from the cache file', exc_info=True)
    return session


def write_aws_cache(cache_file_name: str, session: dict) -> dict:
    ensure_cache_dir()
    cache_path = str(constants.AWSUME_CACHE_DIR) + '/' + cache_file_name
    if os.path.exists(cache_path):
        os.chmod(cache_path, 0o600)
    else:
        open(cache_path, 'a').close()
        os.chmod(cache_path, 0o600)
    logger.debug('Cache file path: ' + cache_path)
    expiration = session['Expiration'].astimezone(dateutil.tz.tzlocal())
    expiration = expiration.strftime('%Y-%m-%d %H:%M:%S')
    try:
        json.dump({
            **session,
            'Expiration': expiration,
        }, open(cache_path, 'w'), indent=2, default=str)
    except:
        logger.debug('There was an error writing to the cache file', exc_info=True)
    session['Expiration'] = datetime.strptime(expiration, '%Y-%m-%d %H:%M:%S')
    return session


def valid_cache_session(cache_session: dict) -> bool:
    if cache_session.get('Expiration'):
        session_expiration = cache_session['Expiration']
        if type(cache_session['Expiration']) == str:
            session_expiration = datetime.strptime(session_expiration, '%Y-%m-%d %H:%M:%S')
        if session_expiration <= datetime.now():
            logger.debug('Cache session has expired')
            return False
    if 'AccessKeyId' not in cache_session:
        return False
    if 'SecretAccessKey' not in cache_session:
        return False
    if 'SessionToken' not in cache_session:
        return False
    logger.debug('Cache session is valid')
    return True
