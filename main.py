import pandas as pd
import plotly
import plotly.express as px
import math
import plotly.graph_objects as go
import gpx_util as gu

pd.set_option('display.max_rows', 500)
path = 'gpx_files/15.gpx'
path2 = '/Users/sylvainmougel/Downloads/2021-05-30_379583043_Bouchaux.gpx'
path3 = 'gpx_files/huez.gpx'
path4 = 'gpx_files/Zoncolan.gpx'


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
    for i in range(len(alt_gain) - 10):
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

    if ends:
        if starts[-1] > ends[-1]:
            climbs.append((starts[-1], len(alt_gain) -1))

    return starts, ends, climbs




if __name__ == '__main__':

    dists, alts, delta_dist, delta_alt = gu.parse_gpx(path)

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
    df2 = pd.DataFrame({'dist': new_tot_dist, 'delta_dists': new_dists, 'delta_alt': new_alts, 'average_alt':average_alt_gain, 'average_climb': average_climb})
    #df2['pente'] = df2['delta_alt'] / df2['delta_dists'] * 100
    print(df2.tail(500))
    fig = go.Figure()

    for c in climbs:
        s, e = c
        s2, e2 = climbs[1]
        dist = [d - new_tot_dist[s] for d in new_tot_dist[s:e]]
        alt = [a - new_tot_alt[s] for a in new_tot_alt[s:e]]
        fig.add_trace(go.Scatter(x=dist, y=alt, mode="lines"))

    dists2, alts2, delta_dist2, delta_alt2 = gu.parse_gpx(path2)
    dists3, alts3, delta_dist3, delta_alt3 = gu.parse_gpx(path3)
    dists4, alts4, _, _ = gu.parse_gpx(path4)

    fig.add_trace(go.Scatter(x=dists2, y=[a - alts2[0] for a in alts2], mode="lines", name="Bouchaux"))
    fig.add_trace(go.Scatter(x=dists3, y=[a - alts3[0] for a in alts3], mode="lines", name="Huez"))
    fig.add_trace(gu.create_trace_from_gpx(path4))
    fig.add_trace(gu.create_trace_from_gpx('gpx_files/loze.gpx'))
    fig.add_trace(gu.create_trace_from_gpx('gpx_files/Angliru.gpx'))
    fig.add_trace(gu.create_trace_from_gpx('gpx_files/Herpie.gpx'))

    fig.write_html('bouchaux.html')

#fig = px.line(x=d1, y=alt1)
#fig.add_trace()
