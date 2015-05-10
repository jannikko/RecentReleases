from requests import make_get_request, read_response, parse_json
from flask import session
import datetime
import re
import queue
import concurrent.futures

q = queue.Queue()


class ArtistsIterator():
    def __iter__(self):
        self.first_query = query_tracks(50, 0)
        self.first_iteration = True
        self.total = self.first_query['total']
        self.query_size = 50
        self.offset = 50
        return self

    def __next__(self):
        if self.first_iteration and self.total > 0:
            self.first_iteration = False
            return extract_artists_from_tracks_json(self.first_query)
        elif self.total - self.offset > 0:
            tracks = query_tracks(self.query_size, self.offset)
            self.offset += self.query_size
            return extract_artists_from_tracks_json(tracks)
        else:
            raise StopIteration


def get_artists():
    artists = dict()
    for artist in ArtistsIterator():
        artists.update(artist)
    return artists


def query_tracks(limit, offset):
    request_verb = {'limit': limit,
                    'offset': offset,
                    }
    request_header = {
        'Authorization': session['access_token']
    }
    response = make_get_request('https://api.spotify.com/v1/me/tracks/?', verb=request_verb,
                                header=request_header)
    response = read_response(response)
    tracks = parse_json(response)
    return tracks


def query_albums(artist_id):
    limit = {
        'limit': 50
    }
    response = make_get_request('https://api.spotify.com/v1/artists/%s/albums?' % artist_id, verb=limit)
    response = read_response(response)
    return parse_json(response)


def get_artists_albums(artists):
    artist_albums = list()
    for artist_id in artists.keys():
        albums_json = query_albums(artist_id)
        albums = extract_albums_from_json(albums_json)
        artist_albums += albums
    return artist_albums


def extract_albums_from_json(albums):
    return [item['id'] for item in albums['items']]


def extract_artists_from_tracks_json(tracks):
    artists = dict()
    for item in tracks['items']:
        for artist in item['track']['artists']:
            artists[artist['id']] = artist['name']
    return artists


def get_recent_releases(albums):
    releases = set()
    start = 0
    counter = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        for end in range(20, len(albums), 20):
            executor.submit(query_albums_info, albums[start:end])
            start = end
            counter += 1
        for i in range(counter):
            try:
                releases.update(filter_recent_releases(q.get(timeout=5)))
            except queue.Empty as e:
                continue
    return releases


def query_albums_info(albums):
    if len(albums) <= 20:
        list_string = ",".join(albums)
        verb = {
            'ids': list_string
        }
        response = make_get_request('https://api.spotify.com/v1/albums?', verb)
        response = read_response(response)
        q.put(parse_json(response))


def filter_recent_releases(albums_info):
    return ((album['name']) for album in albums_info['albums'] if
            re.match('^\d\d\d\d-\d\d-\d\d$', album['release_date'])
            and datetime.datetime.strptime(album['release_date'],
                                           '%Y-%m-%d') > datetime.datetime.now() - datetime.timedelta(14))


def chain_functions(*args, parameter):
    result = args[0](parameter)
    if len(args) > 1:
        for function in args:
            result = function(result)
    return result