from flask import Flask, render_template, redirect, url_for, make_response, session
import flask
import urllib.request
import random
import string
import json
import urllib.parse


app = Flask(__name__)
app.secret_key = 'Z\xd5\xd9\xd7\xc2\x12Ol1x\x05`\xe8\xe8\xd3\x9a}\x98\xd7e|\x89\x82\n'
client_id = '21037bf080ad4603ad6632c7538a3189'
client_secret = 'efc7417b8dfc4dd885f1bb3eb68e6c22'
redirect_uri = 'http://localhost:8000/callback'
state_key = 'spotify_auth_state'


def get_random_number(length):
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(length))


@app.route('/login')
def login():
    state = get_random_number(16)
    login_query = build_login_query(state)
    login_verb = urllib.parse.urlencode(login_query)
    response = make_response(redirect('https://accounts.spotify.com/authorize/?' + login_verb, code=302))
    response.set_cookie(state_key, state)
    return response


def query_saved_tracks_json(limit, offset):
    tracks_query = build_tracks_query(limit, offset)
    raw_tracks_response = make_get_request('https://api.spotify.com/v1/me/tracks/?', verb=tracks_query,
                                           access_token=True)
    tracks_response = read_response(raw_tracks_response)
    tracks = parse_json(tracks_response)
    return tracks


def extract_artists_from_tracks_json(tracks_json):
    artists = dict()
    for item in tracks_json['items']:
        for artist in item['track']['artists']:
            artists[artist['id']] = artist['name']
    return artists


def get_all_artists():
    limit = 50
    offset = 0
    artists = dict()
    tracks_left = 0
    while True:
        if tracks_left > limit or not tracks_left:
            # get the maximum amount
            tracks_json = query_saved_tracks_json(limit, offset)
            if not tracks_left:
                tracks_left = tracks_json['total']
            offset += limit
            tracks_left -= limit
            new_artists = extract_artists_from_tracks_json(tracks_json)
            artists.update(new_artists)
        else:
            # get the left over artists
            tracks_json = query_saved_tracks_json(tracks_left, offset)
            new_artists = extract_artists_from_tracks_json(tracks_json)
            artists.update(new_artists)
            break
    return artists


def get_similar_artists(artists):
    pass


@app.route('/')
def index():
    if 'access_token' in session:
        artists = get_all_artists()
        return render_template('index.html', logged_in=True, artists=artists)
    else:
        return render_template('index.html', logged_in=False)


@app.route('/callback')
def authenticate():
    code = flask.request.args.get('code')
    state = flask.request.args.get('state')
    state_in_cookie = flask.request.cookies.get(state_key)
    if not state or state != state_in_cookie:
        return redirect(url_for('index'))
    else:
        client_response = make_response(redirect(url_for('index')))
        client_response.set_cookie(state_key, '', expires=0)
        token_query = build_token_query(code)
        raw_token_response = make_post_request('https://accounts.spotify.com/api/token', token_query)
        if raw_token_response.getcode() == 200:
            token_response = read_response(raw_token_response)
            tokens = parse_json(token_response)
            set_session(tokens)
            return client_response
        else:
            return client_response


def set_session(tokens):
    session['access_token'] = tokens['token_type'] + ' ' + tokens['access_token']
    session['refresh_token'] = tokens['refresh_token']


def read_response(encoded_response):
    return encoded_response.read().decode('UTF-8')


def parse_json(response):
    return json.loads(response)


def build_login_query(state):
    login_query = {'response_type': 'code',
                   'client_id': client_id,
                   'scope': 'user-library-read',
                   'redirect_uri': redirect_uri,
                   'state': state
                   }
    return login_query


def build_token_query(code):
    token_query = {
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    return token_query


def build_tracks_query(limit, offset):
    tracks_query = {
        'limit': limit,
        'offset': offset,
    }
    return tracks_query


def make_post_request(endpoint, body, access_token=False):
    urlencoded_query = urllib.parse.urlencode(body)
    byte_query = urlencoded_query.encode('ASCII')
    req = urllib.request.Request(endpoint, byte_query)
    if access_token:
        print(session['access_token'])
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


'''
@app.route('/refresh_token')
def refresh_token():

'''

if __name__ == '__main__':
    app.run(port=8000, debug=True)
