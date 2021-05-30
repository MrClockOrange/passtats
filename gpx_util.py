from lxml import etree
import math
import plotly.graph_objects as go

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

def parse_gpx(path):
    root = etree.parse(path)
    lats = []
    longs = []
    alts = []
    dists = [0]
    dist = 0
    delta_dist = [0]
    delta_alt = [0]
    prev = ()
    for elem_ in root.getroot()[1]:
        print(elem_.tag)
        if 'trkseg' in elem_.tag:
            print('found')
            for elem in elem_:
                lat = float(elem.get('lat'))
                lon = float(elem.get('lon'))
                alt = float(elem[0].text)
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

    return dists, alts, delta_dist, delta_alt


def create_trace_from_gpx(path):
    dists, alts, _, _ = parse_gpx(path)
    name = path.split('/')[-1]
    return go.Scatter(x=dists, y=[a - alts[0] for a in alts], mode="lines", name=name[:-4])

