import json
import webbrowser
from os import listdir
from os.path import isfile, join
from pylab import *

import numpy as np
from pathlib import Path
import random
import community as cm
import folium
import polyline
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt



def stuff():
    base_path = Path(__file__).parent
    file_path = (base_path / "../Data/Master/network.csv").resolve()
    with open(file_path, 'r') as f:
        df = pd.read_csv(file_path)
    print(len(df.index))
    print(df['weight'].max())
    print(len(list(df['Source'].unique())))
    df1 = random.sample(list(set(list(df['Source'].unique()) + list(df['Target'].unique()))), 1000)
    print(len(df1))
    df = df[df['Source'].isin(df1)]
    df = df.loc[df['weight'] > 5]
    print(len(df.index))
    G = nx.from_pandas_edgelist(df, source="Source", target='Target', edge_attr='weight')
    part = cm.best_partition(G)
    betweenness_dict = nx.betweenness_centrality(G)
    nx.set_node_attributes(G, betweenness_dict, 'betweenness')

    mod = cm.modularity(part, G)
    print(mod)
    values = [part.get(node) for node in G.nodes()]
    nx.draw_kamada_kawai(G, cmap=plt.get_cmap('jet'), node_color=values, node_size=30, with_labels=False)
    plt.show()


def minMax(xMin, xMax, yMin, yMax, x, y):
    xMin = min(xMin, min(x))
    xMax = max(xMax, max(x))
    yMin = min(yMin, min(y))
    yMax = max(yMax, max(y))
    return xMin, xMax, yMin, yMax


def segmentmap():
    base_path = Path(__file__).parent
    file_path = (base_path / "../Data/Master/SegmentMetaData").resolve()
    segments = [int(f[:-5]) for f in listdir(file_path) if isfile(join(file_path, f))]
    segmentPolys = []
    polys = []
    segmentPoints = []
    uniqueModularity = {0}

    file_path = (base_path / f"modularity2.csv").resolve()
    with open(file_path, "r") as read_it:
        modularityDf = pd.read_csv(read_it)
    print(modularityDf)
    maxSize = 0
    for segment in segments:
        file_path = (base_path / f"../Data/Master/SegmentMetaData/{segment}.json").resolve()
        with open(file_path, "r") as read_it:
            data = json.load(read_it)


            loc = data['start_latlng']
            size = data['effort_count']

            if size > maxSize:
                maxSize = size
            if segment in modularityDf.values:
                modularity_class = modularityDf.loc[modularityDf["Id"] == segment, 'modularity_class'].values[0]+1
            else:
                modularity_class=0
            uniqueModularity.add(modularity_class + 1)

            segmentPoints.append((loc, size,modularity_class))
            polys.append((polyline.decode(data['map']['polyline']),modularity_class))
            segmentPolys.append(list(zip(*polyline.decode(data['map']['polyline']))))
    centroid = [
        np.mean([poly[0][0] for poly in segmentPolys]),
        np.mean([poly[1][0] for poly in segmentPolys])
    ]
    m = folium.Map(location=centroid, tiles="cartodbpositron", zoom_start=13)
    cmap = plt.get_cmap('Paired', len(uniqueModularity))
    lst_colors = [matplotlib.colors.rgb2hex(cmap(i)) for i in range(cmap.N)]
    print([[j*255 for j in cmap(i)] for i in range(cmap.N)])
    #lst_colors = ['#%06X' % np.random.randint(0, 0xFFFFFF) for i in range(len(uniqueModularity))]

    legend_html = """<div style="position:fixed; bottom:10px; left:10px; border:2px solid black; z-index:9999; font-size:14px;">&nbsp;<b>Clusters:</b><br>"""
    for i in uniqueModularity:
        legend_html = legend_html + """&nbsp;<i class="fa fa-circle 
         fa-1x" style="color:""" + lst_colors[list(uniqueModularity).index(i)] + """">
         </i>&nbsp;""" + str(i) + """<br>"""
    legend_html = legend_html + """</div>"""
    m.get_root().html.add_child(folium.Element(legend_html))

    for poly in polys:
        folium.PolyLine(poly[0], color=lst_colors[poly[1]]).add_to(m)

    for points in segmentPoints:
        color = lst_colors[points[2]]
        folium.Circle(location=points[0],
                      radius=(points[1] / maxSize) * 1000 + 100,
                      fill=True,
                      #fill_opacity=1,
                      color=color, ).add_to(m)

    def auto_open(path):
        html_page = f'{path}'
        m.save(html_page)
        # open in browser.
        new = 2
        webbrowser.open(html_page, new=new)

    auto_open("map.html")


def main():
    segmentmap()


if __name__ == '__main__':
    main()
