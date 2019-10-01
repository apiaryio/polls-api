from django.test import Client as DjangoClient

import refract
from refract.json import JSONSerialiser
from refract.contrib.apielements import HTTPTransaction, HTTPRequest, HTTPResponse, Asset


def element_from_request(method, path, data, content_type, **extra):
    request = HTTPRequest()
    request.attributes['method'] = method
    request.attributes['href'] = path
    # FIXME headers

    if data:
        # FIXME "binary" in element, if we can't serialise content as unicode
        asset = Asset(content=data.decode('utf-8'))
        asset.classes = ['messageBody']
        asset.attributes['contentType'] = content_type
        request.append(asset)

        headers = refract.Object(content={ 'Content-Type': content_type })
        headers.element = 'httpHeaders'
        request.attributes['headers'] = headers

    return request


def element_from_response(response):
    element = HTTPResponse()
    # FIXME headers, data
    element.attributes['statusCode'] = response.status_code

    if len(response.items()) > 0:
        headers = refract.Object(content=[])
        headers.element = 'httpHeaders'

        for (key, value) in response.items():
            headers.content.append(refract.Member(key=refract.refract(key), value=refract.refract(value)))

        element.attributes['headers'] = headers

    return element


TRANSACTIONS = refract.Array()
class Client(DjangoClient):
    def generic(self, method, path, data='', content_type='application/octet-stream', **extra):
        response = super(Client, self).generic(method, path, data=data, content_type=content_type, **extra)

        transaction = HTTPTransaction(content=[
            element_from_request(method, path, data, content_type, **extra),
            element_from_response(response),
        ])

        TRANSACTIONS.append(transaction)

        print('')
        print(JSONSerialiser().serialise(transaction))

        return response


def save_transactions():
    print(JSONSerialiser().serialise(TRANSACTIONS))
