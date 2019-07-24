import base64
import xmltodict
import json

import colorama
from . safe_print import safe_print

def parse_assertion(assertion: str) -> list:
    roles = []
    response = xmltodict.parse(base64.b64decode(assertion))
    attributes = response.get('saml2p:Response', {}).get('saml2:Assertion', {}).get('saml2:AttributeStatement', {}).get('saml2:Attribute', {})
    if not attributes:
        safe_print('Unable to parse SAML assertion', colorama.Fore.RED)
        exit(1)
    for attribute in [_ for _ in attributes if _.get('@Name', '') == 'https://aws.amazon.com/SAML/Attributes/Role']:
        for value in attribute['saml2:AttributeValue']:
            roles.append(value['#text'])
    return roles
