from lxml import etree
import pandas as pd
import plotly
import plotly.express as px
path = '15.gpx'

root = etree.parse(path)
#%%
lats = []
longs = []
alts = []
for elem in root.getroot()[1][2]:
    lats.append(float(elem.get('lat')))
    longs.append(float(elem.get('lon')))
    alts.append(int(elem[0].text))
    #print(elem.get('lat'), elem.get('lon'), elem[0].text)
df = pd.DataFrame(data={'lat':lats,'long':longs,'alt':alts})
print(df)

fig = px.line(y=alts)
fig.show()