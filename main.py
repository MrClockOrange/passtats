from lxml import etree
import pandas as pd
import plotly
import plotly.express as px
import math
import plotly.graph_objects as go

pd.set_option('display.max_rows', 500)
path = '15.gpx'


def compute_dist(lat1, lon1, lat2, lon2):
    earth_radius = 6371000
    phi1 = lat1 * math.pi / 180
    phi2 = lat2 * math.pi / 180
    delta_phi = (lat2 - lat1) * math.pi / 180
    delta_lon = (lon2 - lon1) * math.pi / 180
    a = math.sin(delta_phi / 2) * math.sin(delta_phi / 2) + math.cos(phi1) * math.cos(phi2) * math.sin(
        delta_lon / 2) * math.sin(delta_lon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = earth_radius * c
    return d


def compute(raw_dists, raw_alts):
    new_dists = []
    new_alts = []
    new_alts_delta = []
    new_tot_dist = []
    new_tot_alt = []
    j, delta_d, delta_a, tot, totalt = 0, 0, 0, 0, 0
    while j < len(raw_dists) :
        delta_d += raw_dists[j]
        delta_a += raw_alts[j]
        j += 1
        if delta_d > 200 or j == len(raw_dists) - 1:
            new_dists.append(delta_d)
            new_alts_delta.append(delta_a)
            tot += delta_d
            totalt += delta_a
            new_tot_dist.append(tot)
            new_tot_alt.append(totalt)
            new_alts.append(totalt)
            delta_d, delta_a = 0, 0

    return new_tot_dist, new_tot_alt, new_dists, new_alts_delta

def detect_climb(alt_gain):
    starts = []
    ends = []
    was_start = False
    was_end=False
    for i in range(len(alt_gain) - 20):
        if sum(alt_gain[i:i+20]) > 200 and alt_gain[i] > 0:
            if not was_start:
                starts.append(i)
            was_start = True
        elif sum(alt_gain[i:i+20]) < -200 and alt_gain[i]  < 0:
            if not was_end:
                ends.append(i)
            was_end = True
        else:
            was_end = False
            was_start = False

    climbs = []
    current = 0
    for s in starts:
        if s > current:
            found = False
            for e in ends:
                if e > s and not found:
                    climbs.append((s, e))
                    current = e
                    found = True

    if starts[-1] > ends[-1]:
        climbs.append((starts[-1], len(alt_gain) -1))

    return starts, ends, climbs



if __name__ == '__main__':

    root = etree.parse(path)
    lats = []
    longs = []
    alts = []
    dists = [0]
    dist = 0
    delta_dist = [0]
    delta_alt = [0]
    prev = ()
    for elem in root.getroot()[1][2]:
        lat = float(elem.get('lat'))
        lon = float(elem.get('lon'))
        alt = int(elem[0].text)
        lats.append(lat)
        longs.append(lon)
        alts.append(alt)
        if prev:
            prevlat, prevlon = prev
            delta = compute_dist(*prev, lat, lon)
            dist += delta
            delta_dist.append(delta)
            delta_alt.append(alt - prevalt)
            dists.append(dist)
        prev = (lat, lon)
        prevalt = alt

    new_tot_dist, new_tot_alt, new_dists, new_alts = compute(delta_dist, delta_alt)
    window_size = 10
    average_climb = [0] * window_size
    average_alt_gain = [0] * window_size
    for i in range(len(new_alts)-window_size):
        average_alt = sum(new_alts[i:i+window_size])/window_size
        average_dist = sum(new_dists[i:i+window_size])/window_size
        pente_moyenne = average_alt/ average_dist
        average_climb.append(pente_moyenne*100)
        average_alt_gain.append(average_alt)

    print()
    starts, ends, climbs = detect_climb(new_alts)
    print([(new_tot_dist[s], new_tot_dist[e]) for s, e in climbs])
    print([new_tot_dist[s] for s in ends])
    print(starts)
    print(ends)
    print(climbs)
    # print(elem.get('lat'), elem.get('lon'), elem[0].text)
    df = pd.DataFrame(
        {'lat': lats, 'long': longs, 'alt': alts, 'dist': dists, 'delta_dists': delta_dist, 'delta_alt': delta_alt})
    df2 = pd.DataFrame({'dist': new_tot_dist, 'delta_dists': new_dists, 'delta_alt': new_alts, 'average_alt':average_alt_gain, 'average_climb': average_climb})
    #df2['pente'] = df2['delta_alt'] / df2['delta_dists'] * 100
    #print(df2.tail(500))
    fig = go.Figure()

    for c in climbs:
        s, e = c
        s2, e2 = climbs[1]
        dist = [d - new_tot_dist[s] for d in new_tot_dist[s:e]]
        alt = [a - new_tot_alt[s] for a in new_tot_alt[s:e]]
        fig.add_trace(go.Scatter(x=dist, y=alt, mode="lines"))
    fig.show()

#fig = px.line(x=d1, y=alt1)
#fig.add_trace()
