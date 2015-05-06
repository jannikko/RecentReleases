from requests import make_get_request, read_response, parse_json


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
            return extract_artists_from_tracks(self.first_query)
        elif self.total - self.offset > 0:
            tracks = query_tracks(self.query_size, self.offset)
            self.offset += self.query_size
            return extract_artists_from_tracks(tracks)
        else:
            raise StopIteration


def get_artists():
    artists = dict()
    for artist in ArtistsIterator():
        artists.update(artist)
    return artists


def query_tracks(limit, offset):
    tracks_query = build_tracks_query(limit, offset)
    raw_tracks_response = make_get_request('https://api.spotify.com/v1/me/tracks/?', verb=tracks_query,
                                           access_token=True)
    tracks_response = read_response(raw_tracks_response)
    tracks = parse_json(tracks_response)
    return tracks


def extract_artists_from_tracks(tracks):
    artists = dict()
    for item in tracks['items']:
        for artist in item['track']['artists']:
            artists[artist['id']] = artist['name']
    return artists


def build_tracks_query(limit, offset):
    return {
        'limit': limit,
        'offset': offset,
    }


def get_similar_artists(artists):
    pass