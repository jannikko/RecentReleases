import urllib.parse
import urllib.request
import http.client
import json


def read_response(encoded_response):
    try:
        contents = encoded_response.read()
    except http.client.IncompleteRead as e:
        contents = encoded_response.partial()
    return contents.decode('UTF-8')


def parse_json(response):
    return json.loads(response)


def make_post_request(endpoint, body, header=None):
    urlencoded_query = urllib.parse.urlencode(body)
    byte_query = urlencoded_query.encode('ASCII')
    req = urllib.request.Request(endpoint, byte_query)
    if header:
        for k, v in header.items():
            req.add_header(k, v)
    return urllib.request.urlopen(req)


def make_get_request(endpoint, verb=None, header=None):
    if verb:
        endpoint = endpoint + '?' + urllib.parse.urlencode(verb)
    req = urllib.request.Request(endpoint)
    if header:
        for k, v in header.items():
            req.add_header(k, v)
    return urllib.request.urlopen(req)