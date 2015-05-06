import views
import unittest
import json


class testJson(unittest.TestCase):
    file = open(
        '/media/jannik/Daten/Linux/Dropbox/Linux/Python/SpotifyRecentReleases/RecentReleases/testfiles/tracks_query.json',
        encoding='utf-8')
    tracks_json = json.loads(file.read())
    expected_result = {
        "6dEtLwgmSI0hmfwTSjy8cw": 'Real Friends',
        "6DL8cHjzUa0J8WSH2EWDMX": 'The Cinema'
    }

    def test_extract_artists_from_tracks_json_equals_expected_artists(self):
        tracks_result = views.extract_artists_from_tracks_json(self.tracks_json)
        print(tracks_result)
        self.assertDictEqual(self.expected_result, tracks_result)


if __name__ == '__main__':
    unittest.main()