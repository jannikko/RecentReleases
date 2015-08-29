from flask import Flask, render_template, redirect, url_for, make_response, session
from artists import get_artists
from requests import make_post_request, read_response
import flask
import urllib.request
import random
import string
import urllib.parse
import base64
import datetime
import json

app = Flask(__name__)
app.secret_key = 'XXX'  # flask secret_key
CLIENT_ID = '21037bf080ad4603ad6632c7538a3189'  # Spotify API ID
CLIENT_SECRET = 'XXX'  # Spotify API Secret
redirect_uri = 'http://localhost:8000/callback'
state_key = 'spotify_auth_state'


def get_random_number(length):
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(length))


@app.route('/login')
def login():
    #  The state can be useful for correlating requests and responses. Because your redirect_uri can be guessed,
    #  using a state value can increase your assurance that an incoming connection is the result of an
    #  authentication request, security measure against cross-site request forgery
    state = get_random_number(16)
    login_query = {'response_type': 'code',
                   'client_id': CLIENT_ID,
                   'scope': 'user-library-read',
                   'redirect_uri': redirect_uri,
                   'state': state
                   }
    login_verb = urllib.parse.urlencode(login_query)
    response = make_response(redirect('https://accounts.spotify.com/authorize/?' + login_verb, code=302))
    response.set_cookie(state_key, state)
    return response


@app.route('/')
def index():
    if 'access_token' in session:
        if session['expires_in'] < datetime.datetime.now():
            return redirect(url_for('refresh_token'))
        return render_template('index.html', logged_in=True)
    else:
        return render_template('index.html', logged_in=False)


@app.route('/get_artists')
def artists_json():
    return json.dumps(list(get_artists()))


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
        token_query = {
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        raw_token_response = make_post_request('https://accounts.spotify.com/api/token', token_query)
        if raw_token_response.getcode() == 200:
            token_response = read_response(raw_token_response)
            tokens = json.loads(token_response)
            set_session(tokens)
            return client_response
        else:
            return client_response


@app.route('/refresh_token')
def refresh_token():
    request_body = {
        'grant_type': 'refresh_token',
        'refresh_token': session['refresh_token']
    }
    client_credentials = CLIENT_ID + ':' + CLIENT_SECRET
    client_credentials = client_credentials.encode('ascii')
    request_header = {
        'Authorization': 'Basic ' + base64.b64encode(client_credentials).decode('ascii')
    }
    response = make_post_request('https://accounts.spotify.com/api/token', request_body, request_header)
    response = read_response(response)
    tokens = json.loads(response)
    set_session(tokens)
    return redirect(url_for('index'))


def set_session(tokens):
    if tokens.get('access_token'):
        session['access_token'] = tokens['token_type'] + ' ' + tokens['access_token']
        session['expires_in'] = datetime.datetime.now() + datetime.timedelta(0, int(tokens['expires_in']))
    if tokens.get('refresh_token'):
        session['refresh_token'] = tokens['refresh_token']


if __name__ == '__main__':
    app.run(port=8000, debug=True)
