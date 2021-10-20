
from pathlib import Path
import random
import community as cm
from networkx.algorithms import community

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
def main():
    base_path = Path(__file__).parent
    file_path = (base_path / "../Data/Master/network.csv").resolve()
    with open(file_path, 'r') as f:
        df = pd.read_csv(file_path)
    print(len(df.index))
    print(df['weight'].max())
    print(len(list(df['Source'].unique())))
    df1=random.sample(list(set(list(df['Source'].unique())+list(df['Target'].unique()))),1000)
    print(len(df1))
    df=df[df['Source'].isin(df1)]
    df=df.loc[df['weight'] > 5]
    print(len(df.index))
    G=nx.from_pandas_edgelist(df,source="Source",target='Target',edge_attr='weight')
    part = cm.best_partition(G)
    betweenness_dict = nx.betweenness_centrality(G)
    nx.set_node_attributes(G, betweenness_dict, 'betweenness')

    mod = cm.modularity(part, G)
    print(mod)
    values = [part.get(node) for node in G.nodes()]
    nx.draw_kamada_kawai(G, cmap=plt.get_cmap('jet'), node_color=values, node_size=30, with_labels=False)
    plt.show()

if __name__ == '__main__':
    main()