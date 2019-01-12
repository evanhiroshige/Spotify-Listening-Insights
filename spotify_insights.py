import sys
import spotipy
import spotipy.util as util
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, timedelta
import plotly
import plotly.graph_objs as go

scope = 'user-library-read'

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
    results = sp.current_user_saved_tracks(50, offset)
    while len(results['items']) != 0:
        results = sp.current_user_saved_tracks(50, offset)
        items += results['items']
        offset += 50
    items = items[::-1]

    ids = []
    ids_to_date = {}
    for item in items:
        ids.append(item['track']['id'])
        ids_to_date[item['track']['id']] = item['added_at'][:10]

    # for date in ids_to_date.values():
    #     year = date[2:4]
    #     month = date[5:7]
    #     day = date[8:10]
    #     total = day + month *

    print(ids_to_date)
    genres = []
    x = []
    artist_ids = []
    artist_ids_separated = []
    ids_separated = []
    count = 0
    for item in items:
        ids_2 = []
        for artist in item['track']['artists']:
            ids_2.append(artist['id'])
            ids_separated.append(ids[count])
        artist_ids += ids_2
        artist_ids_separated.append(ids_2)
        count += 1

    print(len(ids_separated))
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
    z = 0
    dates = []
    for block in artist_ids_separated:
        for id in block:
            for g in id_to_genre[id]:
                x.append(count)
                y.append(genre_key[g])
                dates.append(ids_separated[z])
        z += 1
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
    id_count = 0
    dates = []
    for block in artist_ids_separated:
        for id in block:
            for g in id_to_genre[id]:
                g_count = 0
                for seed in genre_seeds:
                    if seed == 'hip hop':
                        if 'rap' in g and 'trap' not in g:
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
                for i in range(g_count):
                    dates.append(ids_to_date[ids_separated[id_count]])
                if g_count == 0:
                    x.append(count)
                    y.append(0)
                    dates.append(ids_to_date[ids_separated[id_count]])
        count += 1
        id_count += 1

    d1 = date(int(dates[0][:4]), int(dates[0][5:7]), int(dates[0][8:10]))
    dates_len = len(dates) - 1
    d2 = date(int(dates[dates_len][:4]), int(dates[dates_len][5:7]), int(dates[dates_len][8:10]))
    delta = d2 - d1

    dates_2 = []
    date_to_x = {}
    count = 0
    for i in range(delta.days + 1):
        d3 = d1 + timedelta(i)
        dates_2.append(str(d3))
        date_to_x[str(d3)] = count
        count += 1

    dates_3 = []
    for d in dates:
        dates_3.append(date_to_x.get(d))

    plt.plot(dates_3, y, marker='o', markersize=1, linestyle='')

    plt.yticks(list(range(1, len(genre_seeds))), genre_seeds)
    plt.tick_params(axis='y', which='major', labelsize=3)
    plt.savefig('genre1.pdf')

    plt.show()

    plt.hist2d(dates_3, y, bins=(15, len(genre_seeds)), cmap=plt.cm.Reds)
    plt.yticks(list(range(1, len(genre_seeds))), genre_seeds)
    plt.tick_params(axis='y', which='major', labelsize=3)
    plt.savefig('genre2.pdf')
    plt.show()

    # plt.hist2d(dates_3, y, bins=(150, len(genre_seeds)), cmap=plt.cm.Reds)
    # plt.yticks(list(range(1, len(genre_seeds))), genre_seeds)
    # plt.tick_params(axis='y', which='major', labelsize=3)
    # plt.savefig('genre3.pdf')
    # plt.show()

    # z = np.zeros((max(x), len(y)))
    # z_count = np.zeros((np.math.floor(max(x) / 7) + max(x) % 7, len(genre_seeds)))
    # print(z_count.shape)
    # count = 0
    # for i in x:
    day_count = 0
    z = []
    acc = 0
    yesterday = None
    x_pos = 0
    z_col = [0] * (len(genre_seeds) + 1)
    print(dates)
    for i in range(len(dates)):
        day = dates[i]
        val = y[i]
        tomorrow = None
        if i != len(dates) - 1:
            tomorrow = dates[i + 1]
        if not yesterday:
            yesterday = day
            count += 1
        elif yesterday != day:
            day_count += 1

        z_col[val] += 1
        yest_date = date(int(yesterday[:4]), int(yesterday[5:7]), int(yesterday[8:10]))
        d = date(int(day[:4]), int(day[5:7]), int(day[8:10]))
        if d.weekday() == 6:

            if tomorrow and day != tomorrow:
                z_col = [x / day_count for x in z_col]
                z.append(z_col)
                z_col = [0] * (len(genre_seeds) + 1)
                day_count = 0
        yesterday = day
    z = np.transpose(z)

    data = [
        go.Heatmap(
            z=z,
            colorscale='Jet',
        )
    ]
    # layout = go.Layout(
    #     title='GitHub commits per day',
    #     xaxis=dict(ticks='', nticks=36),
    #     yaxis=dict(ticks='')
    # )
    fig = go.Figure(data=data)
    plotly.offline.plot(fig, filename='heatmap.html')

    date_to_week = {}
    count = 0
    for day in dates_2:
        d = date(int(day[:4]), int(day[5:7]), int(day[8:10]))
        date_to_week[day] = count
        if d.weekday() == 6:
            count += 1
    day = dates_2[-1]
    d = date(int(day[:4]), int(day[5:7]), int(day[8:10]))
    if d.weekday() != 6:
        count += 1

    print(date_to_week)
    z = list([[0 for i in range(len(genre_seeds) + 1)] for i in range(count)])

    for i in range(len(dates)):
        day = dates[i]
        val = y[i]
        k = date_to_week.get(day)

        z[k][val] += 1
        print(day, k, val, z[k][val])
    l = list([0 for i in range(10)])
    print(l)
    print(z)
    print(z[0][0], z[1][0], z[100][0])

    z = np.transpose(z)
    data = [
        go.Heatmap(
            z=z,
            colorscale='Jet',
        )
    ]
    # layout = go.Layout(
    #     title='GitHub commits per day',
    #     xaxis=dict(ticks='', nticks=36),
    #     yaxis=dict(ticks='')
    # )
    fig = go.Figure(data=data)
    plotly.offline.plot(fig, filename='heatmap2.html')





else:
    print("Can't get token for", username)
