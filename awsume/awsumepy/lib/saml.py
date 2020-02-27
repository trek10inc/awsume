import base64
import json

try:
    import xmltodict
except:
    xmltodict = False

import colorama
from . safe_print import safe_print
from . exceptions import SAMLAssertionParseError, ValidationException


def parse_assertion(assertion: str) -> list:
    if not xmltodict:
        raise ValidationException(message='SAML option not installed, try installing awsume[saml]')

    roles = []
    response = xmltodict.parse(base64.b64decode(assertion))

    if response.get('saml2p:Response') is not None:
        attributes = response.get('saml2p:Response', {}).get('saml2:Assertion', {}).get('saml2:AttributeStatement', {}).get('saml2:Attribute', {})
        attribute_value_key = 'saml2:AttributeValue'
    else:
        attributes = response.get('samlp:Response', {}).get('saml:Assertion', {}).get('saml:AttributeStatement', {}).get('saml:Attribute', {})
        attribute_value_key = 'saml:AttributeValue'

    if not attributes:
        raise SAMLAssertionParseError()

    for attribute in [_ for _ in attributes if _.get('@Name', '') == 'https://aws.amazon.com/SAML/Attributes/Role']:
        if isinstance(attribute[attribute_value_key], list):
            for value in attribute[attribute_value_key]:
                roles.append(value['#text'])
        else:
            value = attribute[attribute_value_key]
            roles.append(value['#text'])

    return roles
