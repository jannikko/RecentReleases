$.getJSON('get_artists', function (artists) {
    if (artists) {
        var albums = get_artists_albums(artists);
        var recent_releases = get_recent_releases(albums);
    }
});

function get_artists_albums(artists) {
    var artist_albums = [];
    for (var artist_id in artists) {
        var albums = query_albums(artist_id);
        if (albums) {
            albums = extract_albums_from_json(albums);
            artist_albums = artist_albums.concat(albums)
        }
    }
    return artist_albums;
}

function query_albums(artist_id) {
    var albums;
    $.ajax({
        type: 'GET',
        async: false,
        url: 'https://api.spotify.com/v1/artists/' + artist_id + '/albums',
        success: function (data) {
            albums = data;
        }
    });
    return albums;
}

function extract_albums_from_json(albums_json) {
    var albums = [];
    var item_list = albums_json['items'];
    for (var i = 0; i < item_list.length; i++) {
        albums.push(item_list[i]['id']);
    }
    return albums;
}

function get_recent_releases(albums) {
    var recent_releases = new Array();
    var start = 0;
    for (var end = 20; end < albums.length; end += 20) {
        var album_info = query_albums_info(albums.slice(start, end));
        recent_releases = recent_releases.concat(filter_recent_releases(album_info));
        start = end;
    }
    return recent_releases;
}
function filter_recent_releases(albums_info) {
    var current_date = new Date();
    var recently_released_albums = [];
    var albums_list = albums_info['albums'];
    for (var i = 0; i < albums_list.length; i++) {
        var album = albums_list[i];
        var parts = album['release_date'].split('-');
        if (parts.length == 3) {
            var release_date = new Date(parts[0], parts[1], parts[2]);
            if (release_date > current_date - 14) {
                recently_released_albums.push(album['name']);
            }
        }
    }
    ;
    return recently_released_albums;
}


function query_albums_info(albums) {
    var albums_string = albums.join(',');
    var albums_data;
    $.ajax({
        type: 'GET',
        async: false,
        url: 'https://api.spotify.com/v1/albums',
        data: {ids: albums_string},
        success: function (data) {
            albums_data = data;
        }
    });
    return albums_data;
}