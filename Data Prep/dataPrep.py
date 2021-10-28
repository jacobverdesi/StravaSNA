import ast
import math
from os import listdir
from os.path import join, isfile
from pathlib import Path
import pandas as pd
from itertools import combinations


def progress(numerator,denominator, width=30):
    """
    simple progress meter display
    :param percent:
    :param width:
    :return:
    """
    left = int(width * numerator/denominator)
    right = width - left
    print('\r',numerator,'/',denominator,' [', '#' * left, ' ' * right, ']', f' {(numerator/denominator)*100:.0f}%', sep='', end='', flush=True)
def ncr(n, r):
    f = math.factorial
    return f(n) // f(r) // f(n - r)

def createFullNetwork():
    """
    For each segment in Data/Master/Segments get all combinations of athletes and add 1 to weight
    converts dictionary of (source,target) to df with weight
    saves df to Data/Networks/fullNetwork
    :return: network df
    """
    base_path = Path(__file__).parent
    file_path = (base_path / "../Data/Master/Segments").resolve()
    currentSegments = sorted([int(f[:-4]) for f in listdir(file_path) if isfile(join(file_path, f))])
    print("Total segments: ",len(currentSegments))
    masterDict={}
    count=0
    for segment in currentSegments:
        count+=1
        file_path = (base_path / f"../Data/Master/Segments/{segment}.csv").resolve()
        athlete_list = combinations(pd.read_csv(file_path)['athlete_id'], 2)
        for i in list(athlete_list):
            if i in masterDict.keys():
                masterDict[i] += 1
            elif i[::-1] in masterDict.keys():
                masterDict[i[::-1]] += 1
            else:
                masterDict[i] = 1
        progress(count,len(currentSegments))
    print()
    network = pd.Series(masterDict).reset_index()
    print("Network size: ",len(network.index))

    network.columns = ["Source", "Target", "weight"]
    network.to_csv(f"../Data/Networks/fullNetwork.csv")
    return network

def getFullNetwork(new=False):
    base_path = Path(__file__).parent
    if(new):
        return createFullNetwork()
    else:
        return  pd.read_csv((base_path / f"../Data/Networks/fullNetwork.csv").resolve())

def createEgoNetwork(seed, n, neighbors=None):
    if neighbors is None:
        neighbors = set()
    base_path = Path(__file__).parent
    file_path = (base_path / "../Data/Master/Segments").resolve()
    currentSegments = [int(f[:-4]) for f in listdir(file_path) if isfile(join(file_path, f))]
    print(len(currentSegments))
    count=0
    for segment in currentSegments:
        file_path = (base_path / f"../Data/Master/Segments/{segment}.csv").resolve()
        segmentDf=pd.read_csv(file_path)

        if(seed in segmentDf['athlete_id'].unique()):
            neighbors.update(segmentDf['athlete_id'].unique())
        #count += int(seed in segmentDf['athlete_id'].unique())
        #print(neighbors)
        #athlete_list = combinations(pd.read_csv(file_path)['athlete_id'], 2)
       # print(segmentDf)
    neighbors.remove(seed)

    print(len(neighbors))
#     return df


def main():
    #createEgoNetwork(45406272,2)
    network=getFullNetwork(True)
    # print(network)
    # network=network.loc[network['weight'] > 1]
    # print(network)
    # network.to_csv(f"../Data/Master/networkW1.csv",index=False)
    # network = network.loc[network['weight'] > 30]
    # network.to_csv(f"../Data/Master/networkW30.csv",index=False)
    # network = network.loc[network['weight'] > 50]
    # network.to_csv(f"../Data/Master/networkW50.csv",index=False)
    # network = network.loc[network['weight'] > 80]
    # network.to_csv(f"../Data/Master/networkW80.csv", index=False)
if __name__ == '__main__':
    main()
