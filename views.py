from flask import Flask, render_template, redirect, url_for, request, make_response, Response, session
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import random
import string
import json
import os


app = Flask(__name__)
app.secret_key = 'XXX'
my_client_id = '21037bf080ad4603ad6632c7538a3189'
my_secret = 'XXX'
redirect_uri = 'http://localhost:8000/callback'

stateKey = 'spotify_auth_state'


def getRandomNumber(length):
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(length))


@app.route('/login')
def login():
    state = getRandomNumber(16)
    scope = 'user-read-private user-read-email'
    authorization_url = urlencode({'response_type': 'code',
                                   'client_id': my_client_id,
                                   'scope': scope,
                                   'redirect_uri': redirect_uri,
                                   'state': state
                                   })
    resp = make_response(redirect('https://accounts.spotify.com/authorize/?' + authorization_url, code=302))
    resp.set_cookie(stateKey, state)
    return resp


@app.route('/')
def index():
    if 'access_token' in session and 'refresh_token' in session:

        access_token = session['access_token']
        refresh_token = session['refresh_token']

        return render_template('index.html', logged_in=True)
    else:
        return render_template('index.html', logged_in=False)


@app.route('/callback', methods=['GET'])
def authenticate():
    code = request.args.get('code')
    state = request.args.get('state')
    storedState = request.cookies.get(stateKey)
    if not state or state != storedState:
        return redirect(url_for('index'))
    else:
        url = "https://accounts.spotify.com/api/token"
        data = urlencode({
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'client_id': my_client_id,
            'client_secret': my_secret
        })
        byte_data = data.encode('ASCII')
        req = Request(url, byte_data)
        resp = urlopen(req)

        response = make_response(redirect(url_for('index')))
        response.set_cookie(stateKey, '', expires=0)

        if resp.getcode() == 200:
            message = resp.read().decode('ASCII')
            json_obj = json.loads(message)

            session['access_token'] = json_obj['access_token']
            session['refresh_token'] = json_obj['refresh_token']

            return response
        else:
            return response


'''
@app.route('/refresh_token')
def refresh_token():
'''

if __name__ == '__main__':
    app.run(port=8000, debug=True)
