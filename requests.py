import urllib.parse
import urllib.request
from flask import session
import json


def read_response(encoded_response):
    return encoded_response.read().decode('UTF-8')


def parse_json(response):
    return json.loads(response)


def make_post_request(endpoint, body, access_token=False):
    urlencoded_query = urllib.parse.urlencode(body)
    byte_query = urlencoded_query.encode('ASCII')
    req = urllib.request.Request(endpoint, byte_query)
    if access_token:
        req.add_header('Authorization', session['access_token'])
    response = urllib.request.urlopen(req)
    return response


def make_get_request(endpoint, verb=None, header=None, access_token=False):
    if verb:
        endpoint = endpoint + urllib.parse.urlencode(verb)
    req = urllib.request.Request(endpoint)
    if header:
        for k, v in header:
            req.add_header(k, v)
    if access_token:
        req.add_header('Authorization', session['access_token'])
    response = urllib.request.urlopen(req)
    return response