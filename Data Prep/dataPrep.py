import ast
from pathlib import Path
import pandas as pd


def main():
    base_path = Path(__file__).parent
    file_path = (base_path / "../Data/Master/segmentList.txt").resolve()
    with open(file_path, 'r') as f:
        segments_list = dict(ast.literal_eval(f.read()))
    masterDf = pd.DataFrame(columns=["athlete_id", "segment"])
    for segment_id in segments_list.keys():
        if segments_list[segment_id]:
            file_path = (base_path / f"../Data/Master/Segments/{segment_id}.csv").resolve()
            athelete_list = pd.read_csv(file_path)['athlete_id'].to_frame()
            athelete_list = athelete_list.assign(segment=segment_id)
            masterDf = masterDf.append(athelete_list)
    masterDf = masterDf.groupby("athlete_id")['segment'].apply(list)
    print(masterDf)


if __name__ == '__main__':
    main()
