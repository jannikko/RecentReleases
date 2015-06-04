var albums_queue = [];
var releases_queue = [];
var album_requests = 0;
var releases_requests = 0;
var max_request_size = 20;
var length;

String.prototype.capitalizeFirstLetter = function () {
    return this.charAt(0).toUpperCase() + this.slice(1);
};


$.getJSON('get_artists', function (artists) {
    album_requests = artists.length;
    get_artists(artists);
});


var i = 0;
function get_artists(artists) {
    if (i < artists.length) {
        $.ajax({
            type: 'GET',
            url: 'https://api.spotify.com/v1/artists/' + artists[i] + '/albums',
            success: function (data) {
                var albums = extract_albums_from_json(data);
                for (var i = 0; i < albums.length; i++) {
                    if ($.inArray(albums[i], albums_queue) === -1) {
                        albums_queue.push(albums[i]);
                    }
                }
                albums_request_success();
            },
            error: function () {
                --album_requests;
            }

        });
        i++;
        setTimeout(get_artists(artists), 500);
    }
}

function albums_request_success() {
    if (--album_requests === 0) {
        releases_requests = Math.floor(albums_queue.length / max_request_size);
        get_recent_releases();
    }
}

function extract_albums_from_json(albums_json) {
    var albums = [];
    var item_list = albums_json['items'];
    for (var i = 0; i < item_list.length; i++) {
        albums.push(item_list[i]['id']);
    }
    return albums;
}
var start = 0;
var end = 20;
function get_recent_releases() {
    if (end < albums_queue.length) {
        var sliced = albums_queue.slice(start, end);
        var albums_string = sliced.join(',');
        start = end;
        end += 20;
        $.ajax({
            type: 'GET',
            url: 'https://api.spotify.com/v1/albums',
            data: {ids: albums_string},
            success: releases_request_success,
            error: function () {
                --releases_requests;
            }
        });
        setTimeout(get_recent_releases(), 500);
    }
}

function releases_request_success(data) {
    releases_queue = releases_queue.concat(filter_recent_releases(data));
    if (--releases_requests === 0) {
        var albums = [];
        for (var i = 0; i < releases_queue.length; i++) {
            if ($.inArray(releases_queue[i]['name'].toLowerCase(), albums) === -1) {
                albums.push(releases_queue[i]['name'].toLowerCase());
                append_album_to_html(releases_queue[i]);
            }
        }
    }
}


function append_album_to_html(album) {
    var releases_div = document.getElementById('releases_container');
    var post_row = document.createElement("div");
    var post_col = document.createElement("div");
    post_col.setAttribute('class', 'col-md-5');
    post_row.setAttribute('class', 'row vertical-center-row post-container');
    var img = document.createElement("img");
    img.setAttribute('src', album['cover']);
    post_col.appendChild(img);
    var post_content = document.createElement('div');
    post_content.setAttribute('class', 'col-md-7 center');
    var name = document.createTextNode(album['album_type'] + ': ' + album['artist'] + ' - ' + album['name']);
    post_content.appendChild(name);

    post_row.appendChild(post_col);
    post_row.appendChild(post_content);
    releases_div.appendChild(post_row);
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
                var artists = [];
                for (var x = 0; x < album['artists'].length; x++) {
                    artists.push(album['artists'][x]['name']);
                }
                if (artists.length > 5) {
                    artists = "Various Artists"
                } else {
                    artists = artists.join(', ')
                }
                var album_obj = {
                    'album_type': album['album_type'].capitalizeFirstLetter(),
                    'artist': artists,
                    'name': album['name'],
                    'cover': album['images'][1]['url']
                };
                recently_released_albums.push(album_obj);
            }
        }
    }
    return recently_released_albums;
}


