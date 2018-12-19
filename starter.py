import sys
import spotipy
import spotipy.util as util
import numpy as np
import matplotlib.pyplot as plt

scope = 'user-top-read'

if len(sys.argv) > 3:
    username = sys.argv[1]
    client_id = sys.argv[2]
    client_secret = sys.argv[3]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()

token = util.prompt_for_user_token(username, scope, client_id=client_id,
                                   client_secret=client_secret, redirect_uri='http://localhost/')

if token:
    sp = spotipy.Spotify(auth=token)
    offset = 0
    items = []
    ids = []
    results = sp.current_user_saved_tracks(50, offset)
    while len(results['items']) != 0:
        results = sp.current_user_saved_tracks(50, offset)
        items += results['items']
        offset += 50
    items = items[::-1]
    for item in items:
        ids.append(item['track']['id'])

    offset = 0
    features = []
    while offset < len(ids):
        offset2 = 100
        if offset2 + offset > len(ids):
            offset2 = len(ids) - offset
        features += sp.audio_features(ids[offset:offset + offset2])
        offset += 100

    time = np.arange(len(ids))
    dance_values = []
    energy_values = []
    speechiness_values = []
    acousticness_values = []
    liveness_values = []
    valence_values = []
    tempo_values = []

    for i in range(0, len(ids)):
        cur = features[i]
        dance_values.append(cur['danceability'])
        energy_values.append(cur['energy'])
        speechiness_values.append(cur['speechiness'])
        acousticness_values.append(cur['acousticness'])
        liveness_values.append(cur['liveness'])
        valence_values.append(cur['valence'])
        tempo_values.append(cur['tempo'])

    # tempo
    plt.hist2d(time, tempo_values, bins=(12, 40), cmap=plt.cm.Reds)
    plt.show()

    # valence
    plt.hist2d(time, valence_values, bins=(12, 15), cmap=plt.cm.Reds)
    plt.show()

    # energy
    plt.hist2d(time, energy_values, bins=(12, 15), cmap=plt.cm.Reds)
    plt.show()

    # speechiness
    plt.hist2d(time, speechiness_values, bins=(12, 15), cmap=plt.cm.Reds)
    plt.show()

    # dance
    plt.hist2d(time, dance_values, bins=(12, 15), cmap=plt.cm.Reds)
    plt.show()

    # liveness
    plt.hist2d(time, liveness_values, bins=(12, 15), cmap=plt.cm.Reds)
    plt.show()

    genres = []
    x = []
    artist_ids = []
    artist_ids_separated = []
    for item in items:
        ids = []
        for artist in item['track']['artists']:
            ids.append(artist['id'])
        artist_ids += ids
        artist_ids_separated.append(ids)
    artists = []
    offset = 0
    id_to_genre = {}
    while offset < len(artist_ids):
        offset2 = 50
        if offset2 + offset > len(artist_ids):
            offset2 = len(artist_ids) - offset
        artists += sp.artists(artist_ids[offset:offset + offset2])['artists']
        offset += 50
    for artist in artists:
        genres += artist['genres']
        id_to_genre[artist['id']] = artist['genres']
    count = 0
    genre_set = set()
    genre_key = {}
    for genre in genres:
        if genre not in genre_set:
            genre_set.add(genre)
            genre_key[genre] = count
            count += 1
    count = 0
    x = []
    y = []
    for block in artist_ids_separated:
        for id in block:
            for g in id_to_genre[id]:
                x.append(count)
                y.append(genre_key[g])
        count += 1
    plt.plot(x, y, 'o')
    plt.show()
    plt.hist2d(x, y, bins=(40, len(genre_set)), cmap=plt.cm.Reds)
    plt.show()

    genre_seeds = list(map(lambda g: g.replace('-', ' '), sp.recommendation_genre_seeds()['genres']))
    buckets = {}
    count = 1
    for seed in genre_seeds:
        buckets[seed] = count
        count += 1
    count = 0
    x = []
    y = []
    for block in artist_ids_separated:
        for id in block:
            for g in id_to_genre[id]:
                g_count = 0
                for seed in genre_seeds:
                    if seed == 'hip hop':
                        if 'rap' in g:
                            x.append(count)
                            y.append(buckets[seed])
                            g_count += 1
                    elif seed == 'r n b':
                        if 'r&b' in g:
                            x.append(count)
                            y.append(buckets[seed])
                            g_count += 1
                    if seed in g:
                        x.append(count)
                        y.append(buckets[seed])
                        g_count += 1
                if g_count == 0:
                    x.append(count)
                    y.append(0)
        count += 1
    plt.plot(x, y, marker='o', markersize=1, linestyle='')

    plt.yticks(list(range(1, len(genre_seeds))), genre_seeds)
    plt.tick_params(axis='y', which='major', labelsize=3)
    plt.savefig('genre1.pdf')

    plt.show()

    plt.hist2d(x, y, bins=(5, len(genre_seeds)), cmap=plt.cm.Reds)
    plt.yticks(list(range(1, len(genre_seeds))), genre_seeds)
    plt.tick_params(axis='y', which='major', labelsize=3)
    plt.savefig('genre2.pdf')
    plt.show()

    plt.hist2d(x, y, bins=(100, len(genre_seeds)), cmap=plt.cm.Reds)
    plt.yticks(list(range(1, len(genre_seeds))), genre_seeds)
    plt.tick_params(axis='y', which='major', labelsize=3)
    plt.savefig('genre3.pdf')
    plt.show()



else:
    print("Can't get token for", username)
