var albums_queue = [];
var releases_queue = [];
var album_requests = 0;
var releases_requests = 0;


$.getJSON('get_artists', function (artists) {
    for (var i = 0; i < artists.length; i++) {
        album_requests++;
        $.ajax({
            type: 'GET',
            url: 'https://api.spotify.com/v1/artists/' + artists[i] + '/albums',
            success: albums_request_success
        });
    }
});


function albums_request_success(data) {
    var albums = extract_albums_from_json(data);
    albums_queue = albums_queue.concat(albums);
    if (--album_requests === 0) {
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

function get_recent_releases() {
    var start = 0;
    for (var end = 20; end < albums_queue.length; end += 20) {
        releases_requests++;
        var sliced = albums_queue.slice(start, end);
        var albums_string = sliced.join(',');
        $.ajax({
            type: 'GET',
            url: 'https://api.spotify.com/v1/albums',
            data: {ids: albums_string},
            success: releases_request_success
        });
        start = end;
    }
}

function releases_request_success(data) {
    var releases = filter_recent_releases(data);
    for (var i = 0; i < releases.length; i++) {
        if ($.inArray(releases[i], releases_queue) === -1) {
            releases_queue.push(releases[i]);
        }
    }
    if (--releases_requests === 0) {
        for (var i = 0; i < releases_queue.length; i++) {
            var releases_div = document.getElementById('releases');
            var p = document.createElement("p");
            var name = document.createTextNode(releases_queue[i]['name']);
            var img = document.createElement("img");
            img.setAttribute('src', releases_queue[i]['cover']);
            p.appendChild(name);
            p.appendChild(img);
            releases_div.appendChild(p);
        }
        console.log(releases_queue);
    }
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
                var album_obj = {
                    'name': album['name'],
                    'cover': album['images'][1]['url']
                };
                recently_released_albums.push(album_obj);
            }
        }
    }
    return recently_released_albums;
}


