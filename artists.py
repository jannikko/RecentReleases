from requests import make_get_request, read_response, parse_json
from flask import session


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


def extract_artists_from_tracks_json(tracks):
    artists = dict()
    for item in tracks['items']:
        for artist in item['track']['artists']:
            artists[artist['id']] = artist['name']
    return artists
