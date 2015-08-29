var albums_queue;
var releases_queue;
var album_requests;
var releases_requests;
var max_request_size = 20;
var length;
var days = 14;

var loading_image;
var releases_div;

String.prototype.capitalizeFirstLetter = function () {
    return this.charAt(0).toUpperCase() + this.slice(1);
};


function setDays() {
    days = parseInt(document.getElementById('time').value);
    loading_image.style.visibility = "visible";
    reload();
}

function reload() {
    releases_div.innerHTML = "";
    i = 0;
    start = 0;
    end = 20;
    albums_queue = [];
    releases_queue = [];
    album_requests = 0;
    releases_requests = 0;
    $.getJSON('get_artists', function (artists) {
        album_requests = artists.length;
        get_artists(artists);
    });
}


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
                --album_requests;
                check_albums_request();
            },
            error: function () {
                --album_requests;
                check_albums_request();
            }
        });
        i++;
        setTimeout(function() {
    get_artists(artists);
}, 5);
    }
}

function check_albums_request() {
    if (album_requests === 0) {
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
            success: function (data) {
                releases_queue = releases_queue.concat(filter_recent_releases(data));
                --releases_requests;
                check_releases_requests();
            },
            error: function () {
                --releases_requests;
                check_releases_requests();
            }
        });
        setTimeout(get_recent_releases, 5);
    }
}

function check_releases_requests() {
    if (releases_requests <= 0) {
        var albums = [];
        loading_image.style.visibility = "hidden";
        for (var i = 0; i < releases_queue.length; i++) {
            if ($.inArray(releases_queue[i]['name'].toLowerCase(), albums) === -1) {
                albums.push(releases_queue[i]['name'].toLowerCase());
                append_album_to_html(releases_queue[i]);
            }
        }
    }
}


function append_album_to_html(album) {
    var post_row = document.createElement("div");
    var post_col = document.createElement("div");
    var img = document.createElement("img");
    img.setAttribute('src', album['cover']);
    post_col.appendChild(img);
    var post_content = document.createElement('div');
    var name = document.createTextNode(album['album_type'] + ': ' + album['artist'] + ' - ' + album['name']);
    var uri = document.createElement("a");
    uri.setAttribute('href', album['uri']);
    uri.innerHTML = "Open in Spotify";
    post_col.setAttribute('class', 'album_image');
    post_content.appendChild(name);
    post_content.appendChild(document.createElement("br"));
    post_content.appendChild(uri);
    post_content.setAttribute('class', 'album_description');
    post_row.appendChild(post_col);
    post_row.appendChild(post_content);
    post_row.setAttribute('class', 'album');
    releases_div.appendChild(post_row);
}


function filter_recent_releases(albums_info) {
    var current_date = new Date();
    current_date.setDate(current_date.getDate() - days);
    var recently_released_albums = [];
    var albums_list = albums_info['albums'];
    for (var i = 0; i < albums_list.length; i++) {
        var album = albums_list[i];
        var parts = album['release_date'].split('-');
        if (parts.length == 3) {
            var release_date = new Date(parts[0], parts[1], parts[2]);
            if (release_date > current_date) {
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
                    'id': album['id'],
                    'album_type': album['album_type'].capitalizeFirstLetter(),
                    'artist': artists,
                    'name': album['name'],
                    'cover': album['images'][1]['url'],
                    'uri': album['uri']
                };
                recently_released_albums.push(album_obj);
            }
        }
    }
    return recently_released_albums;
}

$(document).ready(function () {
    loading_image = document.getElementById("loading_image");
    releases_div = document.getElementById('releases_container');
    reload();
});

