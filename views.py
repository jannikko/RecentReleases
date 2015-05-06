from flask import Flask, render_template, redirect, url_for, make_response, session
from artists import get_artists
from requests import make_post_request, read_response, parse_json
import flask
import urllib.request
import random
import string
import urllib.parse


app = Flask(__name__)
app.secret_key = 'xxx'
client_id = '21037bf080ad4603ad6632c7538a3189'
client_secret = 'xxx'
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


@app.route('/')
def index():
    if 'access_token' in session:
        artists = get_artists()
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


def build_login_query(state):
    return {'response_type': 'code',
            'client_id': client_id,
            'scope': 'user-library-read',
            'redirect_uri': redirect_uri,
            'state': state
            }


def build_token_query(code):
    return {
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }


'''
@app.route('/refresh_token')
def refresh_token():

'''

if __name__ == '__main__':
    app.run(port=8000, debug=True)
