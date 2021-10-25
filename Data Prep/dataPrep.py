import ast
import math
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
    print('\r',numerator,'/',denominator,' [', '#' * left, ' ' * right, ']', f' {numerator/denominator:.00f}%', sep='', end='', flush=True)
def ncr(n, r):
    f = math.factorial
    return f(n) // f(r) // f(n - r)

def updateNetwork():
    base_path = Path(__file__).parent
    file_path = (base_path / "../Data/Master/segmentList.txt").resolve()
    with open(file_path, 'r') as f:
        segments_list = dict(ast.literal_eval(f.read()))
    masterDict = dict()
    count = 0
    for segment_id in segments_list.keys():
        if segments_list[segment_id]:
            count += 1
            file_path = (base_path / f"../Data/Master/Segments/{segment_id}.csv").resolve()
            athlete_list = combinations(pd.read_csv(file_path)['athlete_id'], 2)
            for i in list(athlete_list):
                if i in masterDict.keys():
                    masterDict[i] += 1
                elif i[::-1] in masterDict.keys():
                    masterDict[i[::-1]] += 1
                else:
                    masterDict[i] = 1
            print(segment_id)
    print(count)
    network = pd.Series(masterDict).reset_index()
    network.columns = ["Source", "Target", "weight"]
    network.to_csv(f"../Data/Master/network.csv")
    return network
def getNetwork():
    base_path = Path(__file__).parent
    file_path = (base_path / "../Data/Master/network.csv").resolve()
    with open(file_path, 'r') as f:
        df = pd.read_csv(file_path,index_col=0)
    return df
def main():
    #network=getNetwork()
    network=updateNetwork()
    print(network)
    network=network.loc[network['weight'] > 1]
    print(network)
    network.to_csv(f"../Data/Master/networkW1.csv",index=False)
    network = network.loc[network['weight'] > 30]
    network.to_csv(f"../Data/Master/networkW30.csv",index=False)
    network = network.loc[network['weight'] > 50]
    network.to_csv(f"../Data/Master/networkW50.csv",index=False)
    network = network.loc[network['weight'] > 80]
    network.to_csv(f"../Data/Master/networkW80.csv", index=False)
if __name__ == '__main__':
    main()
